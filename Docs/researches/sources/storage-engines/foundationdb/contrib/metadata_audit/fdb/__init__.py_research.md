# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py

## Purpose
This file is the vendored FoundationDB Python API package entrypoint used by the metadata audit tools. It delays access to the real binding symbols until the caller selects an API version, and it customizes upstream behavior so the selected version is checked against the loaded `libfdb_c` runtime rather than a hardcoded generated maximum.

The header documents that it is vendored from `bindings/python/fdb/` at commit `2d2a2144f4` and modified for runtime max API version discovery. In this folder it allows the audit scripts to ship with a local binding shim instead of relying entirely on the host Python package.

## Important APIs, Types, And Functions
Module globals expose `__version__` from `fdb.apiversion.FDB_VERSION` and `LATEST_API_VERSION` from `fdb.apiversion.LATEST_API_VERSION`. Before initialization, `open`, `init`, and `transactional` are placeholder functions that raise `RuntimeError` instructing callers to call `api_version()` first.

`is_api_version_selected()` reports whether `_version` has been recorded in module globals, and `get_api_version()` returns it or raises. `_add_symbols(module, symbols)` copies named attributes from implementation modules into this package namespace.

`api_version(ver)` is the central initializer. It prevents selecting two different API versions, rejects versions below 13, imports `fdb.impl`, obtains `header_version` from `fdb.impl._capi.fdb_get_max_api_version()`, validates `ver <= header_version`, calls `fdb_select_api_version_impl(ver, header_version)`, initializes the C API, and then injects core symbols such as `FDBError`, `Future`, `Database`, `Transaction`, `open`, `transactional`, `options`, and `StreamingMode`.

## Control Flow
Importing the package only imports `fdb.apiversion`, sets version constants, and installs guard placeholders. A caller must call `fdb.api_version(version)` before using `fdb.open`, decorators, or transaction classes. On first successful selection, the function loads C API support, publishes binding symbols, handles legacy API compatibility branches, records `_version`, and finally imports and publishes directory and subspace helpers.

For old API versions, `api_version` branches further. Versions below 610 restore legacy `init`, `open_v609`, cluster creation, and `Cluster`; version 13 maps `open_v13`/`init_v13`, restores `Future.get`, and makes `FDBRange` act like an iterator through a local `next` method. Versions above 22 import `fdb.locality`.

## State And Persistence Behavior
The file maintains process-global API selection state through the `_version` global and mutates the package namespace by assigning imported symbols into `globals()`. After selection, repeated calls with the same version are idempotent; calls with a different version raise. There is no file or database persistence here, but the C library selection is effectively process-global and must happen before any FDB operations.

## Dependencies And Integration Points
This module depends on sibling vendored modules `fdb.apiversion`, `fdb.impl`, `fdb.directory_impl`, `fdb.subspace_impl`, and optionally `fdb.locality`. The metadata audit scripts import `fdb` from this package and use `fdb.open`, `fdb.transactional`, `fdb.FDBError`, locality helpers, transaction options, and streaming modes after initialization elsewhere in the vendored binding stack.

The key integration detail is its runtime call to `libfdb_c` for maximum API version. This is intended to keep the bundled Python files usable across installed FoundationDB C libraries rather than being pinned to a generated `LATEST_API_VERSION` value.

## Risks And Edge Cases
The initializer trusts private `fdb.impl._capi` attributes and the exact signature of `fdb_select_api_version_impl`, so vendored file drift against `impl.py` or `libfdb_c` can break initialization. Because symbols are copied into the package namespace, partial initialization failures can leave confusing globals if an unexpected exception occurs after some assignments.

The global API version policy mirrors upstream behavior: choosing the wrong version first cannot be corrected in-process. The high `LATEST_API_VERSION` value in `apiversion.py` is only an advertised upper bound; actual support depends on the loaded C library. Legacy compatibility branches for very old APIs are present but likely unexercised by the metadata audit scripts.

## Test Signals
Simple import tests should confirm that pre-initialization `fdb.open()` and `fdb.transactional()` raise the expected guidance errors, `is_api_version_selected()` is false before selection, and `api_version(ver)` succeeds when `ver` is within the runtime C library max. Negative tests should verify rejection of `ver < 13`, rejection above runtime max, idempotence for repeated same-version calls, and failure for conflicting second versions.

Integration tests for this repository should run at least one audit script far enough to call `fdb.open` against a selected API version, proving that runtime symbol injection, transaction decorators, options, and `FDBError` all resolve from the vendored package.
