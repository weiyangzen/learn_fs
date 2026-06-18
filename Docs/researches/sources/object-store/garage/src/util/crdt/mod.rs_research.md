<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/mod.rs -->
# sources/object-store/garage/src/util/crdt/mod.rs

## Purpose
Module aggregator for Garage CRDT primitives.

## Important APIs, types, and functions
Declares submodules `bool`, `crdt`, `deletable`, `lww`, `lww_map`, `map`, and `option`, then publicly re-exports their primary types and traits.

## Control flow
There is no runtime control flow; Rust module loading and re-exporting build a convenient public API surface.

## State and persistence behavior
No state. The module shapes import paths for all CRDT state stored elsewhere in Garage metadata.

## Dependencies and integration points
Consumed by `garage_util` clients and table schema code that imports `garage_util::crdt::*`.

## Risks and test signals
Adding or removing re-exports is a public API change for workspace crates. Compile tests catch missing exports; CRDT behavior is tested in the submodules.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/mod.rs -->
