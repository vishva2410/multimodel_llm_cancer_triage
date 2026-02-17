## 2025-05-20 - Non-deterministic Upstream Breaks Caching
**Learning:** Caching downstream services (like `CognitiveService`) is impossible if upstream inputs (like `PerceptionService` predictions) are non-deterministic for the same root input (image).
**Action:** Always ensure upstream data generation is deterministic (e.g., seeding RNG with input checksum) before attempting to cache downstream dependent operations.

## 2025-05-20 - Python Module Shadowing in Backend
**Learning:** `backend/app/api/routes.py` shadows `backend/app/api/routes/` directory, making the latter inaccessible as a package. This breaks `main.py` imports.
**Action:** Avoid naming files the same as directories in the same parent package. Use `__init__.py` for package-level exports instead of a sibling file.
