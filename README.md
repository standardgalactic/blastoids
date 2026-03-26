# Blastoids Pic Breeder

[Play Game Protototype](https://standardgalactic.github.io/blastoids/game.html) — *Not working yet*

[Interactive Explorer](https://standardgalactic.github.io/blastoids/) — *Under Development*

An Interactive Evolutionary Selection System Over a Synthetically Generated Image Corpus

[Formal Architecture](https://standardgalactic.github.io/blastoids/blastoids.pdf) 

An evolutionary image selection system with a green monochrome CRT aesthetic. You rate images, the system learns a preference field, breeds new variants from your top-rated images, and gradually shifts what it shows you toward what you seem to want. It runs entirely in the browser with no server required at runtime.

---

## What it does

The system operates in two modes.

**Slideshow mode** shows images one at a time. You classify each as AWESOME, OK, or HORRIBLE using keyboard keys 1/2/3 or the on-screen buttons. Every rating updates a preference vector (called Φ) in the image's embedding space. The sampler uses this vector to bias future draws toward images that resemble what you rated positively, and away from what you rejected.

**Curate mode** pauses autoplay and lets you browse the current top-ranked and worst-ranked sets, inspect bred targets, and navigate manually.

**Breeding** (press B) generates new images derived from your top-rated set. Each bred target is a mutation of one or two parent images — either a soft crop of a region, a pixel blend of two parents, or a color temperature shift. Bred targets have a latent vector interpolated from their parents, so they compete in the same preference field as base images. They appear in the stream at a controlled rate (roughly 22% of draws when the pool is non-empty), decay in score over successive breed generations, and are displayed with their lineage in the HUD.

All state — ratings, preference vector, bred targets, session progress — persists in `localStorage`. Refreshing the page resumes where you left off.

---

## Project structure

```
project/
├── index.html                  — the application
├── generate_embeddings.py      — CLIP embedding generator (run once offline)
├── blastoids_embeddings.json   — generated sidecar (produced by the script)
└── images/
    ├── a/                      — images 1–2500
    │   ├── blastoids_00001_.png
    │   └── ... blastoids_02500_.png
    ├── b/                      — images 2501–5000
    │   ├── blastoids_02501_.png
    │   └── ... blastoids_05000_.png
    └── thumbnails/
        ├── a/                  — 140×140 thumbnails for images in a/
        └── b/                  — 140×140 thumbnails for images in b/
```

The application serves from the project root. It needs a local HTTP server — opening `index.html` as a `file://` URL will fail due to browser CORS restrictions on fetch and canvas cross-origin rules.

---

## Setup

### 1. Serve the project

Any static file server works:

```bash
# Python
python3 -m http.server 8080

# Node
npx serve .

# VS Code: use the Live Server extension
```

Then open `http://localhost:8080` in your browser.

Without embeddings the system runs immediately using pseudo-random latent vectors. It will work — images will be sampled and bred — but the preference field won't correspond to visual similarity. Ratings won't generalize: marking red flowers as AWESOME won't cause other flowers to score higher. For that you need the CLIP embeddings.

### 2. Generate CLIP embeddings (recommended)

Install dependencies:

```bash
pip install open-clip-torch pillow numpy tqdm
```

Run the generator from the project root:

```bash
python3 generate_embeddings.py --blastoids . --out blastoids_embeddings.json
```

This walks `images/a/` and `images/b/` in order, embeds each image using CLIP ViT-B/32, and writes `blastoids_embeddings.json` next to `index.html`. On CPU this takes roughly 8–15 minutes for 5000 images. On GPU it's under a minute.

If the run is interrupted, resume it without re-processing completed images:

```bash
python3 generate_embeddings.py --blastoids . --out blastoids_embeddings.json --resume
```

To produce smaller vectors (faster dot products, ~1.3 MB instead of ~10 MB, retains roughly 85% of the semantic structure):

```bash
python3 generate_embeddings.py --blastoids . --out blastoids_embeddings.json --dim-reduce 64
```

Once `blastoids_embeddings.json` exists next to `index.html`, the browser loads it automatically on startup. The HUD status line confirms the load: `CLIP embeddings loaded: ViT-B-32/openai (512d, 5000 images)`.

---

## Controls

| Key | Action |
|-----|--------|
| `1` | AWESOME — strong positive rating |
| `2` | OK — weak positive rating |
| `3` | HORRIBLE — negative rating |
| `→` | Next image (manual advance) |
| `M` | Toggle slideshow / curate mode |
| `B` | Breed new targets from current top set |
| `T` | Open top-ranked set panel |
| `W` | Open worst-ranked set panel |
| `O` | Open bred targets panel |
| `Space` | Pause / resume autoplay |
| `H` | Hide / show UI (click canvas to restore) |

In slideshow mode, clicking the canvas image counts as OK.

In curate mode, clicking any thumbnail in the side panel jumps to that image.

---

## HUD readouts

**MODE** — current mode and pause state.

**TARGET** — id of the currently displayed image.

**VIEWED** — total images seen this session.

**AWESOME / OK / HORRIBLE** — rating counts.

**FIELD TARGETS (BRED)** — number of bred targets currently in the pool.

**BRED TARGETS SHOWN** — how many bred targets have been displayed.

**PREFERENCE Φ** — magnitude of the preference vector. Zero at session start, grows as you rate. A value above ~0.3 means the field has a clear direction.

**TEMPERATURE** — current sampling temperature. Starts high (exploratory), decays toward a floor as more images are rated. Lower temperature means the sampler favors high-scoring images more strongly.

**FIELD →** — nearest-neighbor proxy for the current field direction. Shows the base image whose embedding best aligns with Φ. Stabilized with hysteresis to prevent flicker. In pseudo-latent mode this is meaningless. With CLIP embeddings it approximates the visual concept the field is converging toward.

**LINEAGE** — for the current image: `BASE CORPUS` if it's an original image, or `mutation-type ← [parent ids]` if it's a bred target.

---

## Breeding mechanics

When you press B, the system:

1. Takes the current top-ranked set filtered to images you've explicitly rated positive
2. Selects pairs weighted by score
3. Applies one of three mutation operators to each pair
4. Generates up to 12 new bred targets per press
5. Adds them to the offspring pool and begins showing them at a controlled rate

**Mutation operators:**

- **Crop** — zooms into a soft-bounded region of parent A. The crop region is encoded into the image's URL fragment at creation time so it's stable across sessions. Probability decreases over successive breed generations as the blend operator becomes more dominant.
- **Blend** — composites parent A and parent B at a random opacity. The latent vector is a matching interpolation. Probability increases over successive breed generations, shifting the population from structural extraction toward semantic combination.
- **Color shift** — applies a warm or cool tint overlay. Mostly cosmetic.

Bred targets decay in score over successive breed generations (configurable via `OFFSPRING_DECAY_RATE`). Targets you have explicitly rated are protected from decay. When the pool approaches its cap, unrated low-scoring targets are pruned to make room for new ones.

---

## CLIP embeddings

Without embeddings, every image has a pseudo-random 16-dimensional vector. The preference field still forms and guides sampling, but similarity is arbitrary — visually unrelated images may have similar vectors.

With CLIP embeddings, each image has a 512-dimensional vector (or fewer if you used `--dim-reduce`) that encodes its visual and semantic content in a shared space trained on image-text pairs. Now similarity is real: images of similar subjects, styles, or compositions cluster together. A preference field built from ratings of architectural photography will generalize to other architectural images even if you haven't rated them.

The embedding sidecar is loaded asynchronously at startup. If it's absent or fails to fetch, the system falls back to pseudo-random vectors silently. If you load a sidecar with a different dimensionality than a previous session (for example switching from pseudo-random 16d to CLIP 512d), any bred targets from the previous session are automatically discarded because their latent vectors are geometrically meaningless in the new space. Base image ratings are preserved.

---

## Tuning

The following constants at the top of `index.html` control system behavior and are safe to adjust:

| Constant | Default | Effect |
|----------|---------|--------|
| `ALIGN_WEIGHT` | `0.55` | How strongly the preference field biases scoring. Higher values cause faster convergence toward your taste; lower values preserve more exploration. |
| `T_MIN` | `0.42` | Minimum sampling temperature. Higher floor means more random exploration even in converged sessions. |
| `T_TAU` | `180` | How many ratings to reach ~63% of temperature decay. Higher values keep the system exploratory for longer. |
| `OFFSPRING_MIX_RATIO` | `0.22` | Fraction of slideshow draws that sample from bred targets. 0 = bred targets only appear by scored chance; 1 = always bred targets. |
| `OFFSPRING_DECAY_RATE` | `0.04` | Score penalty applied to bred targets per breed generation. Higher values cause faster turnover. |
| `AUTOPLAY_MS` | `2800` | Milliseconds per image in slideshow mode. |

---

## Notes on the corpus

Image filenames must follow the pattern `blastoids_NNNNN_.png` with 5-digit zero-padded numbers and a trailing underscore before the extension. Images 1–2500 go in `images/a/`, images 2501–5000 in `images/b/`. Thumbnails mirror this layout under `images/thumbnails/`.

The embedding index in `blastoids_embeddings.json` must match the `IMAGE_URLS` array in `index.html` — index 0 corresponds to `blastoids_00001_.png`, index 4999 to `blastoids_05000_.png`. The `--blastoids` flag in `generate_embeddings.py` guarantees this ordering. If you use a different corpus structure, use `--list` with an explicit ordered file list.
