## 2025-05-27 - Caching Mutable Objects
**Learning:** When using an in-memory cache (like `OrderedDict`) to store mutable objects (like Pydantic models), callers can inadvertently modify the cached instance if a reference is returned directly. This corrupts the cache for future requests.
**Action:** Always return a copy (e.g., `.model_copy()`) when serving from an in-memory cache of mutable objects.
