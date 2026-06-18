<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java -->
# Research: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java

## Purpose
Java recipe example that serializes nested maps/lists to tuple-addressed document leaves.

## Important APIs, Types, And Functions
`toTuples`, `fromTuples`, `insertDoc`, `getDoc`, `getNewID`, `printSubspace`, `clearSubspace`, `smokeTest`

## Control Flow
Smoke test builds nested user data, inserts it under a random or supplied `doc_id`, scans prefixes to reconstruct documents, and prints paths.

## State And Persistence Behavior
Persistent state is stored in fixed FoundationDB subspaces selected by tuple prefixes; most examples clear those subspaces before the smoke scenario. Multi-index examples duplicate values/edges across indexes inside one transaction.

## Dependencies And Integration Points
Depends on Java FoundationDB bindings (`com.foundationdb.*`, `Subspace`, `Tuple`, async `Function`) and a reachable default cluster. Part of the language recipe collection and mirrors concepts also shown in Go, Python, and Ruby recipes.

## Risks And Edge Cases
Example code uses old Java FoundationDB API 300, static global database/subspaces, minimal error handling, and fixed demo subspaces. It is suitable as documentation/sample code, not a reusable library without transaction/error hardening.

## Test Signals
Each class has a `main` or smoke-test path except the skeletal `MicroSpatial`; there is no JUnit harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/java-recipes/MicroDoc.java -->
