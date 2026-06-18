<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/crdt.rs -->
# sources/object-store/garage/src/util/crdt/crdt.rs

## Purpose
Defines Garage's convergence contract for replicated metadata and a helper trait for simple automatically mergeable values.

## Important APIs, types, and functions
`Crdt` requires `merge(&mut self, other)`. `AutoCrdt` is implemented for ordered cloneable values where the maximum value wins; blanket `Crdt` implementation applies to any `AutoCrdt`. `String` and `bool` opt into this simple policy.

## Control flow
Generic CRDT containers call `merge` recursively. For `AutoCrdt`, merge compares values and replaces local state when the remote value is greater.

## State and persistence behavior
No state is stored here; the traits govern how serialized table values converge after reads, writes, sync, and repair.

## Dependencies and integration points
Used throughout Garage table schemas and CRDT modules (`Lww`, maps, options, deletable wrappers). It is central to safe multi-replica metadata reconciliation.

## Risks and test signals
The blanket max-wins policy is only valid for monotonic domains. Accidentally marking a non-monotonic type as `AutoCrdt` can lose information. Tests should check associativity/idempotence/commutativity for every CRDT type.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/crdt.rs -->
