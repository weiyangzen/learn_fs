# sources/sync-backup/bup/lib/bup/_hashsplit.h

## Purpose
Header exposing hashsplit Python extension types and initializer to the `_helpers` module.

## Important APIs, Types, and Functions
Declares `PyTypeObject HashSplitterType`, `PyTypeObject RecordHashSplitterType`, and `int hashsplit_init(void)`.

## Control Flow
No executable control flow in the header. `_helpers.c` calls `hashsplit_init`, then adds the ready types to the module.

## State and Persistence Behavior
No state is owned here; declarations refer to C extension type objects defined in `_hashsplit.c`.

## Dependencies and Integration Points
Requires Python C API types from including translation units. Integrates `_hashsplit.c` with `_helpers.c`.

## Risks and Test Signals
Risks are type declaration/definition mismatch and initialization ordering. Signals are successful module import and availability of `_helpers.HashSplitter` and `_helpers.RecordHashSplitter`.
