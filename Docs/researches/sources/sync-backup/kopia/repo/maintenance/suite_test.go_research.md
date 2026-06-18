# sources/sync-backup/kopia/repo/maintenance/suite_test.go

Purpose: runs format-specific maintenance test suites across supported repository format versions.

Important APIs/types/functions: `formatSpecificTestSuite`, `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`.

Control flow: each top-level test constructs a suite with a format version and runs `suite.Run`.

State/persistence behavior: no direct persistence; it parameterizes other tests that create repository state.

Dependencies/integration: integrates `testify/suite` with Kopia format versions.

Risks/test signals: ensures maintenance behavior is checked against legacy and current formats. Adding a new format version requires extending this suite.
