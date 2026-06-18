# sources/object-store/minio/cmd/namespace-lock_test.go

This file contains focused tests for namespace-lock source attribution and a skipped stress test for local lock map races. It exercises a narrow but important part of the locking implementation rather than full lock semantics.

`TestGetSource` wraps `getSource(2)` and compares the returned string to a hard-coded source location and function name. This validates the formatting contract used in lock diagnostics, but the test is intentionally fragile: adding lines above the test changes the expected line number. The comments warn maintainers about this coupling.

`TestNSLockRace` is skipped by default because it is long. It constructs repeated local `nsLockMap` instances and orchestrates a race in which a timed-out waiter can remove a lock-map entry while other waiters are trying to acquire the same resource. The failure condition is two later lockers acquiring what should be the same exclusive resource. The test includes a manual `lockMapMutex` hold to make the interleaving easier to reproduce.

State is test-local except for runtime scheduling. Dependencies are `runtime`, `testing`, and `time`. Integration value is diagnostic: it documents a known concurrency failure mode in `nsLockMap.lock`/`unlock`. Risk is limited default coverage because the race test is skipped; normal CI only catches `getSource` formatting regressions, not lock races.
