# sources/sync-backup/kopia/repo/blob/suite_test.go

Purpose: drives blob package format-specific tests across all repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite` carries a `format.Version`; `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` invoke `testutil.RunAllTestsWithParam` with the suite.

Control flow: the test utility discovers methods on `formatSpecificTestSuite`, such as retention extension tests in `storage_extend_test.go`, and runs them once per format version.

State and persistence behavior: this file has no state itself; it causes each suite method to create separate test repositories for each format version.

Dependencies/integration: integrates Kopia format version constants with the testutil parameterized-suite runner.

Risks and edge cases: new suite methods automatically run for all versions, which is desirable but can surprise if a test is not format-agnostic.

Test signals: failures identify format-version-specific behavior differences in shared blob/repository tests.
