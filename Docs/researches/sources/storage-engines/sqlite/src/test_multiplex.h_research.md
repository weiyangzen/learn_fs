# sources/storage-engines/sqlite/src/test_multiplex.h

## Purpose

`test_multiplex.h` declares the public interface and file-control opcodes for the multiplex VFS shim.

## Important APIs, types, and functions

It defines `MULTIPLEX_CTRL_ENABLE`, `MULTIPLEX_CTRL_SET_CHUNK_SIZE`, and `MULTIPLEX_CTRL_SET_MAX_CHUNKS`, and declares `sqlite3_multiplex_initialize(const char *zOrigVfsName, int makeDefault)` plus `sqlite3_multiplex_shutdown(int eForce)`.

## Control flow

The documented lifecycle is initialize once with an optional underlying VFS and default flag, use the `multiplex` VFS or SQL `multiplex_control()`, then shut down after all connections close.

## State and persistence behavior

The header owns no state. Its opcodes mutate per-file multiplex state in the implementation, while initialization registers the VFS and auto-extension.

## Dependencies and integration points

It is C/C++ compatible and consumed by `test_multiplex.c` and tests embedding the shim.

## Risks and test signals

Initialize/shutdown are documented as not thread-safe. `SET_MAX_CHUNKS` remains in the API although the implementation no longer enforces a limit. Signals are compile-time API availability and runtime behavior through the paired `.c` file.
