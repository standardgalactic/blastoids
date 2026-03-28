# **Blastoids Pic Breeder**

**Blastoids Pic Breeder** is a browser-based interactive system designed to evolve a personal *aesthetic ecology* through a continuous feedback loop of user evaluation and algorithmic generation.

Unlike conventional curation tools that merely rank a fixed dataset, this system allows the user to sculpt a preference field. That field does not simply describe taste; it actively reshapes the system’s behavior, guiding both what is shown and what can be generated. New images—referred to as *offspring*—emerge directly from this interaction.

---

## **Core Evolutionary Mechanics**

The system operates through a dual-space architecture that separates perception from evaluation.

Pixel space, denoted (\mathcal{X}), is the domain of appearance. It is where images are rendered, displayed, and judged. The visual layer incorporates CRT-inspired effects such as scanlines and phosphor glow, reinforcing the Blastoids aesthetic.

Embedding space, denoted (\mathcal{E}), is the domain of relation. Here, images are represented as vectors derived from CLIP. User feedback is aggregated into a preference vector (\Phi), which defines a direction in this space. Rather than selecting a single target, the system continuously orients itself along this direction, favoring images that align with it.

---

## **The Breeding Process**

The generative core of the system is the breeding layer, through which new images arise from previously selected ones.

Parent images are chosen according to their alignment with the preference field. From these, offspring are constructed by combining latent representations and applying controlled perturbations. The process is stochastic, producing multiple candidates that explore nearby regions of embedding space.

Mutation operates across both representation domains. Cropping extracts and refines structure within a single image. Color shifts alter global visual characteristics without significantly changing semantic position. Blending performs a deeper operation, combining both pixel data and latent vectors to produce images that are simultaneously visual and conceptual hybrids.

Over time, the system exhibits mutation drift. Early behavior emphasizes extraction and refinement, while later behavior increasingly favors synthesis across distinct structures. This induces a gradual transition from localized variation to compositional recombination.

---

## **Sustaining the Ecosystem**

The system is designed to avoid collapse into repetition or narrow fixation.

Sampling is performed over a mixture of two populations: the original corpus and the generated offspring. The presence of the base corpus ensures that the system remains anchored to a stable vocabulary, while the offspring pool introduces variation and expansion.

Memory within the system is selective. Unrated offspring lose influence over time and are eventually removed, preventing accumulation of irrelevant artifacts. In contrast, positively rated images persist and continue to shape the preference field. This creates a structure in which relevance must be continuously maintained rather than statically stored.

A novelty mechanism further ensures ongoing exploration. Images that have been seen frequently lose relative priority, while unseen or rarely seen images are promoted. The system therefore resists stagnation even under strong preference alignment.

---

## **The Result**

The resulting process is weakly autopoietic. It maintains and regenerates its own structure through the interaction of perception, evaluation, and generation.

The user does not merely filter content but participates in shaping the space of possible future images. The system does not converge to a fixed endpoint; instead, it sustains an evolving trajectory within a constrained region of aesthetic possibility.

Over time, a distinct and personalized visual ecology emerges—one that is neither fully predetermined nor entirely random, but continuously co-constructed through interaction.
