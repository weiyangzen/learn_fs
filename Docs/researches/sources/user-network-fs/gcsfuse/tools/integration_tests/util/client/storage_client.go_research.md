# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/storage_client.go

## Purpose

Implements the lower-level GCS storage client layer for integration tests. It selects HTTP/1, gRPC, zonal, TPC endpoint, and key-file authentication modes; centralizes retry behavior; and provides object, bucket, upload, download, appendable writer, listing, and cleanup helpers.

## Important APIs, control flow, and dependencies

Client construction includes `ShouldRetryForTest`, `CreateHttp1StorageClient`, `CreateStorageClient`, `getTokenSrc`, and `CreateStorageClientWithCancel`. Object IO helpers include `ReadObjectFromGCS`, `ReadChunkFromGCS`, `NewWriter`, `WriteToObject`, `CreateObjectOnGCS`, `CreateFinalizedObjectOnGCS`, `DownloadObjectFromGCS`, `DeleteObjectOnGCS`, `DeleteAllObjectsWithPrefix`, `StatObject`, `UploadGcsObjectWithPreconditions`, `UploadGcsObject`, `CopyFileInBucket`, `CopyFileInBucketWithPreconditions`, `NewWriterWithPreconditionsSet`, `AppendableWriter`, `CreateGcsDir`, `BatchUploadFilesWithoutIntermediateDelays`, `ListDirectory`, and `CheckBucketAccess`.

## State, persistence, dependencies, and integration points

The helpers persist and mutate real GCS objects and bucket state. `CreateStorageClient` uses gRPC with bidi reads for zonal buckets, HTTP/1 with HTTP/2 disabled otherwise, optional service account key files, optional billing project through `getBucketHandle`, and `RetryAlways` with custom retry filtering. `NewWriter` detects RAPID storage class and configures appendable writer behavior for zonal runs; non-zonal tests encountering a RAPID bucket return an error.

## Risks and test signals

Risks include broad retries masking real failures, fatal exits in bucket deletion/copy helpers, in-memory reads for large objects, wait/sleep assumptions for zonal size visibility, duplicate entries in combined object/folder listings, and a suspicious no-op `ClearCacheControlOnGcsObject` that mutates fetched attrs without issuing an update. Signals are successful object reads/writes with preconditions, appendable writes at a generation, concurrent prefix deletion/upload without joined errors, and bucket access/listing checks that respect requester-pays and only-dir mount mapping.
