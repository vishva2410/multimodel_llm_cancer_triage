## 2024-05-22 - [FastAPI Async Blocking & Pydantic Caching]
**Learning:** FastAPI `async def` routes run on the main event loop. Blocking synchronous calls (like `generate_content`) freeze the entire server, killing throughput. Always use async clients (e.g., `generate_content_async`) in async routes.
**Action:** Audit all `async def` routes for blocking I/O.

**Learning:** When caching Pydantic models in memory, mutable fields (lists) must be converted to hashable types (tuples) for keys. Cached objects must be returned via `.model_copy()` to prevent consumers from mutating the shared cache state.
**Action:** Use a helper method for cache key generation and always copy on return.
