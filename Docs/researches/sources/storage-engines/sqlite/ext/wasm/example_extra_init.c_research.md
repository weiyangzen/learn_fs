# sources/storage-engines/sqlite/ext/wasm/example_extra_init.c

## Purpose

`example_extra_init.c` is a minimal example of the optional extra initialization hook for canonical SQLite WASM builds. If a file named `sqlite3_wasm_extra_init.c` is present in the main WASM build directory, the build arranges for SQLite to define `SQLITE_EXTRA_INIT=sqlite3_wasm_extra_init` and call it during `sqlite3_initialize()`.

## Important APIs, Types, and Functions

- `int sqlite3_wasm_extra_init(const char *z)`: required hook signature.
- `sqlite3.h`: included so the hook is compiled in the SQLite build context.
- `fprintf(stderr, "%s: %s()\n", __FILE__, __func__)`: observable example side effect.

## Control Flow

During SQLite initialization, the library calls `sqlite3_wasm_extra_init(NULL)` once. This example writes a diagnostic line to stderr and returns `0`, allowing initialization to continue. A nonzero return would make SQLite initialization fail.

## State and Persistence

The example maintains no state and makes no persistent changes. Its only side effect is stderr output during initialization.

## Dependencies and Integration Points

The hook integrates with SQLite's `SQLITE_EXTRA_INIT` mechanism and the WASM build system convention for detecting `sqlite3_wasm_extra_init.c`. It must be compiled into the SQLite WASM module. Stderr routing depends on the embedding module, usually Emscripten `printErr` or a worker stdout/stderr bridge.

## Risks and Edge Cases

- Returning nonzero from a real hook prevents SQLite initialization.
- Heavy work in this hook can affect every SQLite initialization path.
- Hook code must be valid in the WASM build environment and should avoid platform APIs unavailable under Emscripten or the target runtime.

## Test Signals

A build including this hook should emit one stderr line naming the file and function during `sqlite3_initialize()`, then continue to report successful SQLite startup. A negative test can return nonzero and assert that module initialization fails clearly.
