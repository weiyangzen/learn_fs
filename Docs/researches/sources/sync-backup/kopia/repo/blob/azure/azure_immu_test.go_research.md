# sources/sync-backup/kopia/repo/blob/azure/azure_immu_test.go

Purpose: integration test for Azure blob immutability retention behavior.

Important APIs/types/functions: `TestAzureStorageImmutabilityProtection`, `getBlobRetention`, and `getAzureCLI`. The test uses Azure CLI/service calls, Kopia's blob storage API, and environment-provided immutable container credentials.

Control flow: the test is skipped unless immutable Azure test variables and CLI support are available. It creates/opens Azure storage, writes blobs with retention options, verifies retention metadata through Azure APIs, extends retention, attempts deletion paths, and validates behavior expected for protected blobs.

State and persistence behavior: it mutates a real Azure container and blob retention state. Cleanup must account for immutable retention windows, so test data can persist until policies expire.

Dependencies/integration points: exercises `azure.PutBlob`, `ExtendBlobRetention`, delete-marker logic, Azure versioning/immutability APIs, and external credentials/CLI. Risks include flakiness from cloud policy propagation, clock skew around retention dates, and environment leakage. The test is a high-value signal for provider-specific retention semantics that unit tests cannot cover locally.
