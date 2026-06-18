# sources/sync-backup/restic/internal/backend/gs/gs_test.go

Purpose: Integration and benchmark harness for the Google Cloud Storage backend.

Important APIs and functions: `newGSTestSuite` creates the generic backend suite. `TestBackendGS` and `BenchmarkBackendGS` gate execution on project, repository, and credential environment variables.

Control flow and state: Tests parse `RESTIC_TEST_GS_REPOSITORY`, set project ID and unique prefix, and run generic backend tests or benchmarks. They require either `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_ACCESS_TOKEN`.

Dependencies and integration: Uses `internal/backend/test`, `gs.NewFactory`, real GCS credentials, and `internal/test.SkipDisallowed` on skips.

Risks and test signals: Skipped without credentials. When enabled, it validates the GCS backend against the shared backend contract and performance benchmarks.
