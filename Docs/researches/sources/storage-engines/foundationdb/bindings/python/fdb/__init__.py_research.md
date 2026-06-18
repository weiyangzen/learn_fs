# sources/storage-engines/foundationdb/bindings/python/fdb/__init__.py

Purpose: public entry point and API-version gate for the FoundationDB Python binding.

Important APIs and flow: before `api_version`, `open`, `init`, and `transactional` raise clear runtime errors. `api_version(ver)` validates one-time selection, enforces supported version bounds, imports `fdb.impl`, calls the C API selector, improves error messages for unsupported C library versions, initializes the C API, then injects public symbols from `impl`, directory, and subspace modules. It also handles compatibility paths for older API versions, including v13 method aliases and pre-610 cluster/open symbols.

State and persistence: module globals hold `__version__`, `LATEST_API_VERSION`, injected symbols, and `_version`. No database state changes occur until users call injected APIs. Dependencies include generated `fdb.apiversion`, `fdb.impl`, `fdb.locality`, `fdb.directory_impl`, and `fdb.subspace_impl`. Risks include global one-shot version state, dynamic symbol injection obscuring static analysis, and compatibility branches that must remain aligned with impl behavior. Signal is import/version selection behavior and downstream binding tests.
