# sources/storage-engines/wiredtiger/src/conn/api_version.c

## Purpose

`api_version.c` implements the public `wiredtiger_version` API. It returns the compiled WiredTiger version string and optionally writes major, minor, and patch components to caller-provided pointers.

## Important APIs, Types, and Functions

- `wiredtiger_version`: public function returning `WIREDTIGER_VERSION_STRING`.
- Version macros: `WIREDTIGER_VERSION_MAJOR`, `WIREDTIGER_VERSION_MINOR`, `WIREDTIGER_VERSION_PATCH`, and `WIREDTIGER_VERSION_STRING`.

## Control Flow

The function checks each output pointer for NULL before assignment, writes the corresponding macro value when present, and returns the version string unconditionally.

## State and Persistence Behavior

No runtime or persistent state is used. The result is entirely compile-time version metadata.

## Dependencies and Integration Points

The file includes `wt_internal.h` for version macros. `wiredtiger_version` is exposed as part of the public C API and is also assigned to `WT_EXTENSION_API.version` in `conn_api.c`, allowing extensions to query the running library version.

## Risks and Edge Cases

- Callers may pass any subset of NULL output pointers; this is supported.
- Version correctness depends on build-time macro generation.
- Extensions may use this for compatibility checks, so stale or mismatched version macros can cause confusing plugin behavior.

## Test Signals

Tests should call `wiredtiger_version` with all output pointers, with each pointer NULL, and with all pointers NULL. Assertions should compare returned components and string against build metadata.
