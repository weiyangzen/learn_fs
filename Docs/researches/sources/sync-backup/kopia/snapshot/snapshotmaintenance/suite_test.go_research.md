# sources/sync-backup/kopia/snapshot/snapshotmaintenance/suite_test.go

Purpose: drives the snapshot maintenance test suite against multiple repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite`, `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`.

Control flow: each top-level test calls `testutil.RunAllTestsWithParam` with a suite value carrying one `format.Version`, causing the methods in `snapshotmaintenance_test.go` to run for that format.

State and persistence: this file creates no repository state itself; it parameterizes the stateful integration tests.

Dependencies and integration points: ensures snapshot GC and maintenance behavior remains valid across format versions 1, 2, and 3.

Risks and test signals: suite discovery depends on the test utility recognizing methods on `formatSpecificTestSuite`. Failures identify format-specific persistence or maintenance regressions rather than logic isolated to this file.
