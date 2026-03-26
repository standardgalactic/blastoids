#!/usr/bin/env python3
"""
generate_embeddings.py — CLIP embedding generator for Blastoids Pic Breeder
========================================================================

Produces a compact JSON sidecar (blastoids_embeddings.json) mapping each
image index to a normalized CLIP ViT-B/32 embedding vector.

Drop the sidecar next to your index.html. The HTML loader will fetch it
at startup and replace the pseudo-random latent vectors with real ones.
No server required at runtime.

Usage
-----
  # Embed a directory of images (jpg/png/webp/gif):
  python3 generate_embeddings.py --images /path/to/your/images --out blastoids_embeddings.json

  # Embed images listed in a text file (one path per line):
  python3 generate_embeddings.py --list images.txt --out blastoids_embeddings.json

  # Embed picsum-style sequential URLs (matches the default IMAGE_URLS in the HTML):
  python3 generate_embeddings.py --picsum 600 --seed blastoids_ --out blastoids_embeddings.json

  # Resume a partial run (skips already-computed indices):
  python3 generate_embeddings.py --images /path/to/images --out blastoids_embeddings.json --resume

  # Use a different CLIP model (default: ViT-B-32 / openai):
  python3 generate_embeddings.py --images /path --model ViT-L-14 --pretrained openai

Output format
-------------
{
  "model":  "ViT-B-32/openai",
  "dim":    512,
  "count":  600,
  "embeddings": {
    "0": [0.023, -0.041, ...],   // L2-normalized, 512 floats
    "1": [...],
    ...
  }
}

The HTML reads this file once at startup. Indices must match IMAGE_URLS positions.
If an index is missing (e.g. failed download), the HTML falls back to the
pseudo-random vector for that image — so partial runs are safe to load.

Requirements
------------
  pip install open-clip-torch pillow requests tqdm
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import torch
import open_clip
from PIL import Image, UnidentifiedImageError


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Generate CLIP embeddings for Blastoids corpus")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--images",    help="Directory of image files (sorted rglob)")
    src.add_argument("--list",      help="Text file with one image path per line")
    src.add_argument("--picsum",    type=int, metavar="N",
                     help="Embed N picsum.photos images (matches default HTML IMAGE_URLS)")
    src.add_argument("--blastoids", metavar="ROOT",
                     help="Root of the Blastoids project folder. Expects images/a/ and "
                          "images/b/ with filenames blastoids_00001_.png … blastoids_05000_.png. "
                          "Index order matches IMAGE_URLS in the HTML exactly.")

    p.add_argument("--count",      type=int, default=5000,
                   help="Total image count for --blastoids mode (default: 5000)")
    p.add_argument("--split",      type=int, default=2500,
                   help="How many images are in folder a/ (default: 2500)")
    p.add_argument("--seed",       default="blastoids_",
                   help="Picsum seed prefix (default: blastoids_)")
    p.add_argument("--size",       default="960/720",
                   help="Picsum image size (default: 960/720)")
    p.add_argument("--out",        default="blastoids_embeddings.json",
                   help="Output JSON path (default: blastoids_embeddings.json)")
    p.add_argument("--model",      default="ViT-B-32",
                   help="OpenCLIP model name (default: ViT-B-32)")
    p.add_argument("--pretrained", default="openai",
                   help="OpenCLIP pretrained weights (default: openai)")
    p.add_argument("--batch",      type=int, default=32,
                   help="Batch size (default: 32)")
    p.add_argument("--resume",     action="store_true",
                   help="Skip already-computed indices if output file exists")
    p.add_argument("--dim-reduce", type=int, default=None,
                   help="PCA-reduce embeddings to this dimension (optional)")
    return p.parse_args()


# ── IMAGE SOURCES ─────────────────────────────────────────────────────────────

def collect_paths(args):
    """Return list of (index, source) where source is a local path or URL.
    Index 0 must correspond to IMAGE_URLS[0] in the HTML."""

    if args.blastoids:
        # Deterministic ordering that exactly matches the HTML IMAGE_URLS array.
        # Index i (0-based) → image number n = i+1 (1-based).
        # n in [1, split] → images/a/blastoids_NNNNN_.png
        # n in [split+1, count] → images/b/blastoids_NNNNN_.png
        root  = Path(args.blastoids)
        count = args.count
        split = args.split
        paths = []
        missing = []
        for i in range(count):
            n      = i + 1
            folder = 'a' if n <= split else 'b'
            fname  = f"blastoids_{n:05d}_.png"
            fpath  = root / "images" / folder / fname
            if not fpath.exists():
                missing.append(str(fpath))
            paths.append((i, str(fpath)))
        if missing:
            print(f"WARNING: {len(missing)} files not found. First few:")
            for p in missing[:5]:
                print(f"  {p}")
            print("Missing files will use pseudo-random fallback vectors in the HTML.")
        print(f"Blastoids corpus: {count} images ({split} in a/, {count-split} in b/)")
        return paths

    if args.images:
        exts = {".jpg",".jpeg",".png",".webp",".gif",".bmp",".tiff"}
        paths = sorted([
            p for p in Path(args.images).rglob("*")
            if p.suffix.lower() in exts
        ])
        if not paths:
            sys.exit(f"No image files found in {args.images}")
        print(f"Found {len(paths)} images in {args.images}")
        return [(i, str(p)) for i, p in enumerate(paths)]

    if args.list:
        with open(args.list) as f:
            lines = [l.strip() for l in f if l.strip()]
        return [(i, src) for i, src in enumerate(lines)]

    if args.picsum:
        urls = [
            f"https://picsum.photos/seed/{args.seed}{i}/{args.size}"
            for i in range(args.picsum)
        ]
        return [(i, url) for i, url in enumerate(urls)]


# ── IMAGE LOADING ─────────────────────────────────────────────────────────────

_url_cache = {}

def load_image(source: str) -> Image.Image | None:
    try:
        if source.startswith("http"):
            if source in _url_cache:
                return _url_cache[source]
            req = urllib.request.Request(source, headers={"User-Agent": "blastoids-embed/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            img = Image.open(__import__("io").BytesIO(data)).convert("RGB")
            _url_cache[source] = img
            return img
        else:
            return Image.open(source).convert("RGB")
    except (UnidentifiedImageError, Exception) as e:
        print(f"\n  WARN: failed to load {source!r}: {e}", file=sys.stderr)
        return None


# ── EMBED ─────────────────────────────────────────────────────────────────────

def embed_batch(model, preprocess, images: list, device) -> np.ndarray:
    tensors = []
    for img in images:
        try:
            tensors.append(preprocess(img).unsqueeze(0))
        except Exception:
            # fallback: blank image
            tensors.append(torch.zeros(1, 3, 224, 224))
    batch = torch.cat(tensors, dim=0).to(device)
    with torch.no_grad():
        feats = model.encode_image(batch)
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.cpu().float().numpy()


# ── PCA REDUCTION (optional) ─────────────────────────────────────────────────

def pca_reduce(matrix: np.ndarray, target_dim: int) -> np.ndarray:
    """Reduce embedding matrix to target_dim via PCA. Re-normalizes after."""
    print(f"\nApplying PCA: {matrix.shape[1]}→{target_dim} dims ... ", end="", flush=True)
    mean = matrix.mean(axis=0)
    centered = matrix - mean
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    components = Vt[:target_dim]
    reduced = centered @ components.T
    # re-normalize each row
    norms = np.linalg.norm(reduced, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    reduced = reduced / norms
    print(f"done. Explained variance: {(S[:target_dim]**2).sum()/(S**2).sum():.1%}")
    return reduced, mean, components


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    sources = collect_paths(args)

    # Load existing output for --resume
    existing = {}
    if args.resume and os.path.exists(args.out):
        with open(args.out) as f:
            prev = json.load(f)
        existing = prev.get("embeddings", {})
        print(f"Resuming: {len(existing)} indices already computed, skipping those.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {args.model}/{args.pretrained} on {device} ...")
    model, _, preprocess = open_clip.create_model_and_transforms(
        args.model, pretrained=args.pretrained
    )
    model = model.to(device).eval()
    actual_dim = model.encode_image(
        torch.zeros(1, 3, 224, 224).to(device)
    ).shape[-1]
    print(f"Model ready. Embedding dim: {actual_dim}")

    embeddings = dict(existing)
    todo = [(i, src) for i, src in sources if str(i) not in existing]
    print(f"Processing {len(todo)} images (batch size {args.batch}) ...")

    t0 = time.time()
    failed = 0

    for batch_start in range(0, len(todo), args.batch):
        batch_items = todo[batch_start:batch_start + args.batch]
        images, valid_indices = [], []

        for idx, src in batch_items:
            img = load_image(src)
            if img is not None:
                images.append(img)
                valid_indices.append(idx)
            else:
                failed += 1

        if images:
            vecs = embed_batch(model, preprocess, images, device)
            for idx, vec in zip(valid_indices, vecs):
                embeddings[str(idx)] = vec.tolist()

        done = batch_start + len(batch_items)
        elapsed = time.time() - t0
        rate = done / elapsed if elapsed > 0 else 0
        eta = (len(todo) - done) / rate if rate > 0 else 0
        print(
            f"  {done}/{len(todo)}  "
            f"({rate:.1f} img/s, ETA {eta:.0f}s)  "
            f"failed: {failed}",
            end="\r", flush=True
        )

    print(f"\nDone. {len(embeddings)} embeddings computed, {failed} failed.")

    # Optional PCA reduction
    out_dim = actual_dim
    if args.dim_reduce and args.dim_reduce < actual_dim:
        indices_sorted = sorted(embeddings.keys(), key=int)
        matrix = np.array([embeddings[k] for k in indices_sorted])
        reduced, pca_mean, pca_components = pca_reduce(matrix, args.dim_reduce)
        for i, k in enumerate(indices_sorted):
            embeddings[k] = reduced[i].tolist()
        out_dim = args.dim_reduce

    output = {
        "model":      f"{args.model}/{args.pretrained}",
        "dim":        out_dim,
        "count":      len(embeddings),
        "embeddings": embeddings,
    }

    with open(args.out, "w") as f:
        json.dump(output, f, separators=(",", ":"))

    size_mb = os.path.getsize(args.out) / 1e6
    print(f"Saved {args.out} ({size_mb:.1f} MB, {out_dim}-dim vectors)")
    print()
    print("Next step: place blastoids_embeddings.json next to index.html")
    print("The HTML loader will fetch it automatically at startup.")


if __name__ == "__main__":
    main()
