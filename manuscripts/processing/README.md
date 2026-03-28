# **Blastoids Pic Breeder — Technical Specification**

This document provides a formal technical specification for *Blastoids Pic Breeder*, an interactive browser-based system designed for aesthetic exploration and image evolution.

---

## **Core Concept**

Unlike conventional image curation systems that operate over a fixed dataset and merely rank items, Blastoids Pic Breeder constructs a dynamic preference field through user interaction. Each rating contributes to a continuously evolving directional structure in embedding space.

This field does not passively describe preference. It actively reshapes the system’s sampling distribution, influences presentation order, and governs the generation of new images through breeding. The result is a closed-loop process in which user input directly drives the evolution of the visual environment.

---

## **System Components**

### **Preference Field (Φ)**

The preference field is a unit vector in CLIP embedding space. It is constructed as a weighted aggregation of user-rated items, where categorical feedback such as *Awesome*, *OK*, and *Horrible* is mapped to scalar weights and accumulated.

This vector defines a direction of alignment. Items that lie close to this direction in embedding space are more likely to be surfaced, reinforced, and used as the basis for further generation. The field therefore functions as the system’s primary organizing principle.

---

### **Dual-Space Architecture**

The system operates across two coupled representational domains.

Pixel space governs appearance. It is the domain in which images are rendered and perceived by the user. Embedding space governs relation. It is the domain in which similarity, alignment, and preference are computed.

The preference field exists entirely in embedding space, while mutation operators such as crop, blend, and color shift act primarily in pixel space. The blend operator uniquely spans both, interpolating latent vectors while simultaneously combining pixel representations, thereby maintaining coherence between perception and evaluation.

---

### **Breeding Layer**

The system generates new images through a structured breeding process. Offspring are constructed by interpolating the latent vectors of selected parent images and adding controlled noise. The resulting vector is normalized and paired with a corresponding pixel-space transformation.

Mutation behavior evolves over time. Early generations favor operations that extract and refine structure within individual images, such as cropping. As generations increase, blending becomes more prominent, enabling synthesis across distinct regions of embedding space. This induces a developmental trajectory from localized refinement toward compositional recombination.

---

### **Sampling and Non-Collapse**

Image selection is governed by a softmax distribution over a composite score. This score integrates alignment with the preference field, explicit user ratings, novelty terms, and decay penalties.

A strictly positive temperature floor prevents deterministic convergence, ensuring that all items retain nonzero probability of selection. Additionally, sampling is performed over a mixture of two pools: the original corpus and the offspring set. This guarantees that the system remains open to both foundational structure and generated variation.

The result is a non-collapsing dynamic in which exploration persists indefinitely, even under strong preference alignment.

---

### **Persistence and Decay**

The system implements a selective memory structure. Offspring that are not explicitly rated lose influence over time through generation-based decay and are eventually pruned. This prevents accumulation of inert or irrelevant artifacts.

In contrast, rated offspring are preserved and remain active participants in the system’s evolution. The base corpus is immutable and persists as a stable interpretive substrate.

This asymmetry ensures that the system retains continuity while remaining responsive to ongoing interaction.

---

## **Theoretical Context**

The system admits interpretation within several broader theoretical frameworks.

Within an RSVP perspective, the preference field functions as a dynamic constraint that organizes which items become accessible or dominant. It is not merely descriptive but causally active in shaping system behavior.

From the standpoint of TARTAN, the breeding process constitutes recursive generation under historical constraint. New items are derived from prior selections, forming trajectories through both pixel and embedding space.

In relation to the Chain of Memory paradigm, persistence is conditional rather than absolute. Relevance must be continuously renewed either through alignment with the evolving field or through explicit user reinforcement.

---

## **Summary of Invariants**

The system is governed by a set of mathematical invariants that ensure structural stability. All latent vectors are normalized, maintaining consistent geometric interpretation. The preference field is likewise normalized, preserving its role as a directional operator.

The sampling distribution remains strictly positive due to the temperature floor, preventing collapse. The offspring pool is bounded in size, ensuring computational tractability. Rated items persist indefinitely, guaranteeing that validated structure is never lost.

---

## **Interpretation**

Blastoids Pic Breeder can be understood as a minimal, formally defined process in which perception, evaluation, and generation are inseparably coupled.

It does not optimize toward a fixed objective, nor does it merely filter a static dataset. Instead, it sustains an evolving aesthetic ecology shaped by user interaction. The system exhibits weak autopoiesis in the sense that it continuously regenerates its own structure under internally maintained constraints.

The preference field directs attention, the breeding layer expands possibility, and the decay mechanisms enforce relevance. Together, these components produce a dynamic system that remains coherent without becoming static, and exploratory without becoming chaotic.
