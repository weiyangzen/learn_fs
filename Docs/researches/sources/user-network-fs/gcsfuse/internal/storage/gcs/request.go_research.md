# sources/user-network-fs/gcsfuse/internal/storage/gcs/request.go

## Purpose
This file defines the request and response helper types used by the `gcs.Bucket` interface. It is the shared contract between filesystem code, storage backends, fakes, and mocks.

## Important APIs and Types
`CreateObjectRequest` carries name, object metadata, chunk retry/timeout settings, contents, checksum expectations, generation/metageneration preconditions, and chunk callback. `CopyObjectRequest` defines source/destination names, source generation, source metageneration precondition, and destination generation precondition. `MaxSourcesPerComposeRequest` and `MaxComponentCount` encode GCS compose limits. `ComposeObjectsRequest` and `ComposeSource` define composite object creation. `StorageReader` combines `io.ReadCloser` with `ReadHandle`. `ByteRange` models `[Start, Limit)` and formats as `[start, limit)`. `ReadObjectRequest` and `MultiRangeDownloaderRequest` carry name, generation, compressed-read flag, and read handle. `StatObjectRequest`, `GetFolderRequest`, `ListObjectsRequest`, `Listing`, `UpdateObjectRequest`, `DeleteObjectRequest`, `MoveObjectRequest`, and `CreateObjectChunkWriterRequest` define the remaining bucket operations.

## Control Flow and Semantics
The structs are declarative but encode key behavior: zero generation means latest except in preconditions where zero can mean object must not exist; nil pointer update fields mean untouched; empty pointed strings remove fields; metadata update values of nil delete keys; `FetchOnlyFromCache` controls cache-only lookup in stat/list/folder paths; listing delimiter/prefix fields define collapsed runs and pagination ordering; `Projection.String` maps enum values to JSON API projection strings and defaults to `full`.

## State, Dependencies, and Integration
There is no runtime state. Dependencies include `crypto/md5`, `fmt`, `io`, `cloud.google.com/go/storage`, and `google.golang.org/api/storage/v1`. These types are used by bucket implementations, storage utilities, fake tests, mocks, and higher-level filesystem mutation/read flows.

## Risks and Test Signals
Many fields have subtle zero/nil semantics. Pointer preconditions and pointer update fields are especially easy to misuse. `ByteRange` uses `uint64`, while actual backend APIs often use signed offsets/lengths, so conversions must avoid overflow. Cache-only flags must be respected only by implementations with cache support. Compose limits are tested in `bucket_tests.go`.
