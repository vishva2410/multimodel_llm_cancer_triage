## 2025-02-24 - [Synchronous Blocking in Async FastAPI]
**Learning:** Found critical bottleneck where `CognitiveService.analyze` was synchronous and blocking the event loop for 1s+, despite being called from an `async def` path operation. This effectively serialized all requests.
**Action:** Always check `async def` handlers for blocking calls. Converted `CognitiveService.analyze` to async and used `await generate_content_async`. Verified with reproduction script showing 3x speedup.

## 2025-02-24 - [Python Module vs Package Collision]
**Learning:** Found `backend/app/api/routes.py` colliding with `backend/app/api/routes/` directory, causing import failures for `analysis` submodule.
**Action:** Converted `routes.py` to `routes/__init__.py` to make `app.api.routes` a proper package, resolving the conflict while maintaining import paths.
