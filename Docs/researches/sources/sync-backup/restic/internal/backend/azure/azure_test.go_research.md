# sources/sync-backup/restic/internal/backend/azure/azure_test.go

Purpose: Integration and benchmark tests for the Azure backend.

Important APIs and functions: `newAzureTestSuite` configures the generic backend test suite. `TestBackendAzure`, `BenchmarkBackendAzure`, `TestBackendAzureAccountToken`, `TestBackendAzureContainerToken`, and `TestUploadLargeFile` exercise account-key, SAS token, and large upload paths.

Control flow and state: Tests read `RESTIC_TEST_AZURE_*` environment variables, parse repository config, apply environment credentials, set a unique prefix, create the backend, and run generic backend tests or benchmarks. Large upload creates 300 MiB of random data, saves it, then reads several offset/length ranges back for byte comparison.

Dependencies and integration: Uses `internal/backend/test`, `backend.Transport`, `azure.Create`, `options.SecretString`, and real Azure Blob Storage credentials. Cleanup calls `Delete` and `Remove` on test data.

Risks and test signals: Tests are skipped without credentials, so CI signal depends on secret availability. When enabled, they validate credential modes, suite compliance, large block uploads, range reads over block boundaries, and cleanup behavior.
