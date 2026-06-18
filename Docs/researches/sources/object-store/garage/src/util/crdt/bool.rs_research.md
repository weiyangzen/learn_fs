<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/bool.rs -->
# sources/object-store/garage/src/util/crdt/bool.rs

## Purpose
A boolean CRDT where `true` is absorbing, useful for one-way flags that must converge across replicas.

## Important APIs, types, and functions
`Bool(bool)` exposes `new`, `set`, `get`, `From<bool>`, and `Crdt::merge`.

## Control flow
Merging ORs the local and remote value. Once any replica sets the flag, all later merges retain `true`.

## State and persistence behavior
The wrapped boolean is serializable/deserializable and can be stored in table entries. There is no timestamp or tombstone, so it cannot express a reset to false after true is observed.

## Dependencies and integration points
Depends on serde and the Garage `Crdt` trait. It can be nested in larger metadata CRDT structs.

## Risks and test signals
Use only for monotonic flags. Tests should verify false+false stays false and any merge involving true yields true.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/bool.rs -->
