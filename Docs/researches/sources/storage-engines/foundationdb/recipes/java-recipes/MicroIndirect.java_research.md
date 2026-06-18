<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java

## Purpose
Java recipe example that demonstrates directory-layer workspace replacement.

## Important APIs, Types, And Functions
`Workspace.getCurrent`, `getNew`, `replaceWithNew`, `clearSubspace`, `printSubspace`

## Control Flow
Creates current/new directory subspaces, writes demo data, then removes current and moves new to current using chained futures in a transaction.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroIndirect.java -->
