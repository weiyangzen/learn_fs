<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/lib.rs

## Purpose
`lib.rs` is the crate root for the experimental tirocks engine. It documents the goal of reimplementing `engine_traits` with tirocks and reexports the public adapter surface.

## Important APIs, Types, and Functions
The crate enables `feature(test)` under tests and imports `tikv_alloc`. It declares modules for options, vectors, engine, iterator, logger, perf context, properties, snapshot, status, util, and write batch. It publicly reexports engine, iterator, logger, perf context, properties, snapshot type, status, and util modules.

## Control Flow
There is no runtime control flow in the root. Module declarations determine compilation and public API shape.

## State and Persistence Behavior
The root has no state. It initializes allocator linkage through `extern crate tikv_alloc as _`.

## Dependencies and Integration Points
Downstream crates use `engine_tirocks::*` reexports rather than internal module paths. Keeping module API compatible with `engine_rocks` eases replacement work.

## Risks and Edge Cases
Private modules such as `write_batch` are compiled but not reexported directly in this file. Public reexports should be kept deliberate to avoid exposing unfinished internals. The crate is partial by design.

## Test Signals
Compilation and module-level tests validate root wiring. Public API compatibility should be checked against engine-trait consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/lib.rs -->
