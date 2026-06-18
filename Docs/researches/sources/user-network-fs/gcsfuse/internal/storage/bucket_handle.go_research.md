## sources/user-network-fs/gcsfuse/internal/storage/bucket_handle.go

### Purpose
`bucket_handle.go` adapts the project-level `gcs.Bucket` interface to `cloud.google.com/go/storage` object APIs and Cloud Storage Control folder APIs.

### Important APIs, Types, And Functions
`bucketHandle` stores the Go storage bucket handle, bucket name/type, control client, billing project, and write config. Methods implement object reads, creates, chunk writers, appendable writer takeover, finalize/flush, copy, list, update, compose, delete, move, folder CRUD/rename, multi-range download, `Name`, `BucketType`, and `GCSName`. Helpers include `getObjectHandleWithPreconditionsSet`, `getProjectionValue`, and `isStorageConditionsNotEmpty`. Constants format HNS bucket/folder resource names.

### Control Flow
Reads configure range, generation, compressed mode, and optional read handle before calling `NewRangeReader`. Create paths set generation/metageneration preconditions, storage writer attributes, retry/transfer deadlines, progress callbacks, append/finalize behavior for rapid writes, then either copy content and close or return a writer. Appendable takeover requires a generation precondition and checks returned offset against requested offset, mapping mismatch to `gcs.PreconditionError`. List builds `storage.Query`, selects minimal attrs plus `Finalized` for rapid buckets, injects billing project metadata, iterates one page according to `MaxResults`, and separates object attrs from prefix/collapsed runs. Compose, copy, update, delete, and move map request preconditions into storage client conditions. Folder methods call Storage Control API resource names and convert control folders to `gcs.Folder`.

### State, Persistence, And Dependencies
Persistent effects are remote GCS object/folder mutations and uploaded object data. Local state includes bucket type, billing project, and write config. Almost every method defers `gcs.GetGCSError` to normalize storage errors. Dependencies include `cloud.google.com/go/storage`, Storage Control API, `gax`, `grpc/metadata`, config, `storageutil`, iterator, and `internal/storage/gcs`.

### Integration Points
This is the concrete storage backend behind caching, monitoring, throttling, and sync layers. It handles hierarchical namespace folders, rapid/zonal appendable-object semantics, gzip read behavior, read handles, generation preconditions, and billing-project propagation.

### Risks
This adapter is correctness-critical because mismapped preconditions can cause non-idempotent writes or stale data. `CreateAppendableObjectWriter` dereferences `GenerationPrecondition`, so callers must supply it. List pagination intentionally stops at current page when `MaxResults` is nonzero; fake-server behavior differs from real GCS for some prefix/max-result combinations. Multi-range downloader is not wrapped with throttling here. Folder rename waits on a long-running operation and can block until completion.

### Test Signals
`bucket_handle_test.go` extensively covers reads, generation handling, gzip compressed/decompressed reads, delete/stat/copy/create/write/finalize/flush, listing options, update, compose, bucket type detection, and HNS folder APIs using fake storage and mock control clients. Real GCS versioning and some fake-server unsupported precondition/listing behaviors remain gaps.
