# sources/sync-backup/kopia/repo/suite_test.go

Purpose: provides the repository package test harness for running format-specific tests against format versions 1, 2, and 3.

Important APIs/types/functions: `TestMain` delegates to `testutil.MyTestMain`. `formatSpecificTestSuite` stores a `format.Version`. `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` call `testutil.RunAllTestsWithParam`.

Control flow: the test utility reflects over methods on `formatSpecificTestSuite` and runs each with the supplied format version.

State and persistence behavior: no direct persistence; it controls creation of repotesting repositories in suite methods.

Dependencies/integration: depends on `internal/testutil` and `repo/format`. It is the bridge that makes tests in `repository_test.go` execute against multiple repository formats.

Risks: adding suite methods can multiply runtime by three. Format-specific assumptions must be handled inside tests when behavior differs.

Test signals: meta-test harness only; actual assertions live in suite methods.
