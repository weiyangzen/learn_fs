# sources/storage-engines/sqlite/src/test_loadext.c

## Purpose

`test_loadext.c` is a small loadable extension used to test extension loading success and failure paths.

## Important APIs, types, and functions

It uses `sqlite3ext.h`, `SQLITE_EXTENSION_INIT1`, and `SQLITE_EXTENSION_INIT2`. `halfFunc()` returns half its input. `statusFunc()` exposes selected `sqlite3_status()` opcodes by integer or text name. Entry points are `testloadext_init()` and `testbrokenext_init()`.

## Control flow

`testloadext_init()` initializes the extension API pointer and registers `half()`, `sqlite3_status(X)`, and `sqlite3_status(X,RESET)`. `statusFunc()` maps names to opcodes, calls `sqlite3_status()`, and returns current or high-water values. `testbrokenext_init()` sets `*pzErrMsg` to `broken!` and returns failure.

## State and persistence behavior

The extension only registers functions on the connection. `sqlite3_status(..., reset)` may mutate process-global high-water counters.

## Dependencies and integration points

It is compiled as a loadable extension and tests dynamic loader symbol lookup, Windows export decoration, extension API initialization, error-message ownership, and function registration through a loaded module.

## Risks and test signals

Status opcode availability can vary by build. Unknown names return SQL errors. Signals are successful load exposing `half()`/`sqlite3_status()` and failed load surfacing `broken!`.
