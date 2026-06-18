<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/lib.rs -->
# sources/object-store/garage/src/util/lib.rs

## Purpose
Crate root for `garage_util`, exporting shared utility modules.

## Important APIs, types, and functions
Enables tracing macros and declares public modules: `background`, `config`, `crdt`, `data`, `encode`, `error`, `forwarded_headers`, `metrics`, `migrate`, `persister`, `socket_address`, `time`, `tranquilizer`, and `version`.

## Control flow
No runtime control flow; this file defines module visibility and macro import.

## State and persistence behavior
No direct state. It makes persistence, migration, CRDT, and config modules available to the workspace.

## Dependencies and integration points
Every Garage crate importing `garage_util` depends on this public module layout.

## Risks and test signals
Changing module visibility is a workspace API break. Compile of dependent crates is the primary signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/lib.rs -->
