# sources/object-store/minio/cmd/warm-backend-azure.go

Azure Blob Storage implementation of `WarmBackend`. `warmBackendAzure` wraps an `azblob.Client` with bucket/container, prefix, and storage class. It maps storage class to Azure access tier, prefixes destinations, uploads streams with metadata and access tier, downloads byte ranges, deletes blobs, and checks `InUse` by listing one prefixed blob.

`azureConf` validates account, bucket, and exactly one authentication mechanism, then builds either service-principal or shared-key clients. Azure SDK errors are converted to MinIO object errors by service code/status.

State is remote Azure blob data/metadata. Risks include range semantics, unsupported storage classes silently becoming nil tier, prefix handling, incomplete error mapping, and limited use of returned version IDs. No direct tests in this subset cover it.
