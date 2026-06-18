## sources/user-network-fs/gcsfuse/internal/storage/bucket_handle_test.go

### Purpose
`bucket_handle_test.go` is the main behavioral test suite for the Cloud Storage-backed `bucketHandle` adapter.

### Important APIs, Types, And Functions
The suite defines `BucketHandleTest`, `createBucketHandle`, `minObjectsToMinObjectNames`, and `readObjectContent`. It uses `NewFakeStorageWithMockClient`, fake storage data constants, and a mocked Storage Control client. Tests cover reader methods, delete/stat/copy/create/update/compose/list/write/finalize/flush, bucket type detection, and hierarchical folder operations.

### Control Flow
Each test builds a bucket handle with a mocked storage layout, performs an operation through the `gcs.Bucket` contract, and asserts returned data or error type. Writer tests inspect `ObjectWriter` chunk size, object name, progress callback, append/finalize flags, and precondition behavior. Compose tests read source and destination contents to validate concatenation. Folder tests assert exact Storage Control requests for delete, get, rename, and create.

### State, Persistence, And Dependencies
State is a fake GCS server plus mock control client expectations. Some tests create objects or writers and then read back contents. Dependencies include Cloud Storage client types, Storage Control protos, gcsfuse config/storage abstractions, testify suite/mock, and gRPC status codes.

### Integration Points
The suite protects the adapter between internal `gcs` request structs and Google Cloud client calls. It also validates rapid/zonal bucket type flags derived from Storage Control layout responses.

### Risks
Several comments note fake storage limitations: generation/metageneration delete checks, object versioning, `IncludeFoldersAsPrefixes`, and real GCS pagination behavior are not fully modeled. Some compose/list expectations differ from real GCS, so these tests are strongest for adapter mapping and less complete for backend semantics.

### Test Signals
Signals are broad and high value: read ranges/generations/compression/read handles, not-found/precondition errors, writer attributes, finalize failure for existing object with generation zero, listing prefix/delimiter/max-result behavior, update metadata fields, compose edge cases, HNS bucket/folder calls, and bucket type defaults/errors.
