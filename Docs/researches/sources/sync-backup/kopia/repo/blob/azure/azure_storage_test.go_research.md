# sources/sync-backup/kopia/repo/blob/azure/azure_storage_test.go

Purpose: live integration tests for Azure storage construction, cleanup, credential modes, normal blob operations, and invalid configurations.

Important APIs/types/functions: environment constants for Azure credentials, `mustGetOptions`, `createContainer`, `TestCleanupOldData`, `TestAzureStorage`, `TestAzureStorageSASToken`, `TestAzureStorageClientSecret`, `TestAzureStorageClientCertificate`, `TestAzureFederatedIdentity`, `TestAzureStorageInvalidBlob`, `TestAzureStorageInvalidContainer`, `TestAzureStorageInvalidCreds`, and `getBlobCount`.

Control flow: helpers read environment or skip, optionally create containers, then invoke shared `blobtesting` suites against Azure-backed storage. Credential-specific tests construct `azure.Options` for account key, SAS, client secret, certificate, and federated identity. Invalid tests assert failures for bogus blob/container/credentials.

State and persistence behavior: tests create, list, and delete real Azure blobs under configured prefixes/containers. Cleanup tests remove old data according to test-suite rules.

Dependencies/integration points: validates Azure SDK integration, Kopia storage registry, throttling/retrying behavior through shared suites, and environment-managed cloud accounts. Risks include skips hiding coverage in local runs, cloud cost/quota/latency, and retained data after failures. These are the primary regression signals for provider compatibility with the generic blob contract.
