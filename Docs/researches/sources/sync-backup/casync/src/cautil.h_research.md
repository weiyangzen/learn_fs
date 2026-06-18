# sources/sync-backup/casync/src/cautil.h

## Purpose

`cautil.h` declares casync locator and xattr utility functions implemented in `cautil.c`. It is a small shared interface for code that needs to distinguish local paths, SSH paths, and URLs or apply casync-specific name policies.

## Important APIs, Types, and Functions

The header declares `ca_is_url()`, `ca_is_ssh_path()`, `CaLocatorClass`, `ca_classify_locator()`, `ca_strip_file_url()`, `ca_locator_has_suffix()`, `ca_xattr_name_is_valid()`, `ca_xattr_name_store()`, `ca_compressed_chunk_suffix()`, and `ca_locator_patch_last_component()`.

`CaLocatorClass` has path, SSH, URL, and invalid states. The invalid value is negative to fit errno-style validation patterns.

## Control Flow

The header does not implement control flow, but it establishes a two-stage calling pattern: classify a locator, then dispatch to path or remote handling; validate/filter xattrs before storing; optionally rewrite or strip locators before opening.

## State and Persistence Behavior

Most declarations return booleans or allocated strings. Callers are responsible for freeing returned strings from strip/patch functions. The suffix function returns a pointer that may reference process environment storage.

## Dependencies and Integration Points

The header includes `<stdbool.h>` only and is consumed by `casync.c` and storage/archive helpers. It depends on `util.h` only through the implementation, keeping the public include lightweight.

## Risks and Edge Cases

Consumers must not assume `ca_is_url()` accepts every RFC-valid URL or that `ca_is_ssh_path()` is safe for every platform path syntax. Returned allocated strings need ownership handling. `ca_compressed_chunk_suffix()` is process-global through its cached implementation.

## Test Signals

Integration tests should assert consistent classification between this interface and all auto-locator setters in `casync.c`, plus memory-safety checks for returned strings under allocation-failure instrumentation.
