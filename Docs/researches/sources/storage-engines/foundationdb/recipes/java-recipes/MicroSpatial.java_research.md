<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java

## Purpose
Java recipe example that sketches a geospatial label-to-Z-order index.

## Important APIs, Types, And Functions
`xyToZ`, `zToXy`, `setLocation`

## Control Flow
Intended flow converts coordinates to Z value, removes any previous label/Z keys, and writes both `labelZ` and `zLabel` indexes.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
This file is pseudocode-like and not directly compilable as written: coordinate variables and the previous-location conditional are placeholders. `MicroSpatialTest.java` supplies a concrete implementation.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroSpatial.java -->
