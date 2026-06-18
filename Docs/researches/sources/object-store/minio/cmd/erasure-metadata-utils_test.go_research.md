# sources/object-store/minio/cmd/erasure-metadata-utils_test.go

Purpose: validates low-level erasure metadata utility behavior used by the object layer before higher-level object and multipart paths rely on it. The file exercises disk counting, quorum error reduction, object-to-disk distribution hashing, disk shuffling, and evaluation of disks after per-disk errors.

Important APIs and functions under test: `diskCount`, `reduceReadQuorumErrs`, `reduceWriteQuorumErrs`, `hashOrder`, `shuffleDisks`, `evalDisks`, `getRandomDisks`, `initObjectLayer`, `mustGetPoolEndpoints`, and `erasureServerPools`/`xlStorage` setup helpers. `Test_hashOrder` also probes distribution statistically by repeatedly checking which disk ordinal appears first.

Control flow: table-driven tests verify deterministic outputs for small cases, then integration-style setup creates 16 temporary disks and an erasure object layer to test shuffling against actual `StorageAPI` instances. `TestReduceErrs` builds representative error arrays, including wrapped `context.Canceled`, and checks read/write reducers against fixed quorum values. `TestHashOrder` asserts stable rotations for many object names, including unicode and invalid byte input.

State and persistence behavior: the tests create temporary disk roots for object-layer initialization but do not persist application objects. Their main state is in-memory disk slices and temporary storage roots removed with `removeRoots`.

Dependencies and integration points: depends on MinIO test helpers for erasure disks, `StorageAPI`, `xlStorage`, `erasureServerPools`, and quorum errors. These tests are upstream signals for `erasure-metadata.go`, `erasure-object.go`, and multipart/object code paths that assume deterministic disk ordering and meaningful quorum error reduction.

Risks: coverage is strong for deterministic cases but `TestEvalDisks` currently calls `testShuffleDisks`, so it does not appear to directly assert `evalDisks` behavior despite the test name. `Test_hashOrder` logs distribution rather than asserting statistical bounds, making it diagnostic rather than a failing correctness gate.

Test signals: validates that ignored disk errors do not dominate reductions, that wrapped cancellations collapse to `context.Canceled`, and that `hashOrder` returns nil for invalid counts. These signals protect against regressions in object placement and quorum handling.
