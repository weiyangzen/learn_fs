<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java

## Purpose
Java recipe example that implements and smoke-tests the geospatial Z-order index sketched in `MicroSpatial`.

## Important APIs, Types, And Functions
`xyToZ`, `zToXy`, `setLocation`, `getLocation`, `printSubspace`, `main`

## Control Flow
Clears indexes, inserts labels at positions, reads a missing and present label, moves a label, and prints resulting Z locations.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatialTest.java -->
