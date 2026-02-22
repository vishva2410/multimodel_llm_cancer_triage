## 2024-05-23 - [Caching Pydantic Models]
**Learning:** When implementing caching for services with complex inputs (like Pydantic models with list fields), using the input object directly as a cache key fails because lists are unhashable.
**Action:** Always create a deterministic cache key by extracting fields and converting mutable types (lists) to immutable ones (sorted tuples) to ensure order independence. Also, return `model_copy()` of cached Pydantic models to prevent mutation of the cache state by consumers.
