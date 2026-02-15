## 2025-02-18 - [Deterministic Perception Enables Downstream Caching]
**Learning:** Found that `PerceptionService` (upstream) returned random/non-deterministic outputs for the same input, which prevented `CognitiveService` (downstream) from effectively caching LLM calls. Caching relies on stable inputs.
**Action:** Always ensure upstream services produce deterministic outputs (e.g., via seeded RNG with input checksum) if downstream services rely on them for caching keys.
