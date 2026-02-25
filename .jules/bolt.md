## 2025-05-23 - [Blocking I/O in Async Routes]
**Learning:** Synchronous calls to external services (like `google.generativeai.generate_content`) inside `async def` path operations block the event loop, causing requests to be processed sequentially even if concurrent.
**Action:** Always use `await generate_content_async` (or equivalent async methods) or run blocking code in a thread pool (`run_in_executor`) to maintain concurrency.

## 2025-05-23 - [Module vs Package Conflict]
**Learning:** If a file `app/api/routes.py` exists alongside a directory `app/api/routes/`, `import app.api.routes` resolves to the file module. This prevents access to submodules inside the directory (e.g., `app.api.routes.analysis`).
**Action:** Rename `app/api/routes.py` to `app/api/routes/__init__.py` to convert it into a proper package, allowing submodule imports.
