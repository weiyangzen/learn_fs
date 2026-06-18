# sources/sync-backup/kopia/repo/blob/s3/s3_storage_config.go

Purpose: defines the optional S3 `.storageconfig` JSON document that lets a bucket choose S3 storage classes by blob ID prefix.

Important APIs/types/functions: `ConfigName` is `.storageconfig`; `PrefixAndStorageClass` maps a `blob.ID` prefix to a storage-class string; `StorageConfig` holds `BlobOptions`; `Load` and `Save` JSON-decode/encode; `getStorageClassForBlobID` scans options in order and returns the first matching storage class.

Control flow: `newStorageWithCredentials` reads `ConfigName` through the normal `GetBlob` path during S3 storage startup. `putBlob` calls `storageConfig.getStorageClassForBlobID` for every uploaded blob and passes the result to MinIO `PutObjectOptions`.

State and persistence behavior: the config is persisted in the S3 bucket as a hidden Kopia blob and excluded from `ListBlobs`. Prefix ordering is significant because the first match wins; an empty result means default provider storage class.

Dependencies/integration: depends only on JSON, `io`, string prefix checks, and `blob.ID`; it is tightly integrated with `s3_storage.go` upload behavior.

Risks and edge cases: malformed JSON blocks opening the S3 storage. Overlapping prefixes require deliberate order. There is no validation of provider-specific storage-class names here, so invalid names fail later during upload.

Test signals: behavior is indirectly exercised by S3 storage startup and upload tests; direct tests should include malformed JSON, overlapping prefixes, and hidden-list filtering.
