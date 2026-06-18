# sources/sync-backup/restic/internal/backend/b2/b2_test.go

Purpose: Integration and benchmark harness for the B2 backend.

Important APIs and functions: `newB2TestSuite` builds a generic backend test suite with minimal data and delayed-removal wait. `testVars`, `TestBackendB2`, and `BenchmarkBackendb2` gate execution on `RESTIC_TEST_B2_*` environment variables.

Control flow and state: The suite parses `RESTIC_TEST_B2_REPOSITORY`, applies credentials from the test environment, assigns a unique prefix, and runs generic tests or benchmarks.

Dependencies and integration: Uses `internal/backend/test`, `b2.NewFactory`, and real Backblaze B2 credentials. It calls `rtest.SkipDisallowed` when skipped.

Risks and test signals: Skipped without credentials. When enabled, it validates backend interface compliance under B2's delayed deletion behavior.
