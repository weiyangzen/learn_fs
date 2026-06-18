# sources/object-store/minio/cmd/erasure-object_test.go

Purpose: integration-style tests for erasure object behavior across multipart part replacement, deletes, quorum failures, inline data, storage-class quorum derivation, mixed inline metadata, and outdated disk data. The file uses real temporary erasure object layers and fault-injection disk wrappers.

Important APIs and functions under test: `PutObject`, `GetObjectNInfo`, `GetObjectInfo`, `DeleteObject`, `DeleteObjects`, `NewMultipartUpload`, `PutObjectPart`, `objectQuorumFromMeta`, `readAllFileInfo`, and setup helpers `prepareErasure16`, `prepareErasure`, `prepareErasurePools`, `prepareErasureSets32`, `ExecObjectLayerTestWithDirs`. Faults are injected with `newNaughtyDisk`, direct disk nils, data-dir deletion, and storage-class updates.

Control flow: tests create buckets and objects, then mutate disk availability or contents to verify expected error behavior. Delete tests cover invalid names, missing objects, versioned deletes, duplicate delete requests, two-pool version placement, and erasure-set object distribution. No-quorum tests remove data or make disks fail after a few calls, then check read/write errors. Inline tests upload a tiny object then overwrite with larger data to ensure reads remain correct. `TestObjectQuorumFromMeta` uploads objects under multiple storage-class configs and asserts derived read/write quorums. Archive-based and outdated-disk tests verify reads across inconsistent disk states.

State and persistence behavior: creates and removes temporary filesystem roots, writes real `xl.meta` and part data, sometimes reads disk files directly, deletes data directories while preserving metadata, and unzips a sample mixed inline/non-inline `xl.meta` fixture. It mutates global storage-class config and object-layer globals in selected tests.

Dependencies and integration points: depends on MinIO erasure setup helpers, `StorageAPI`, disk mutexes, `naughtyDisk`, storage-class package, filesystem paths, crypto random input, MD5 checks, and `testdata/xl-meta-inline-notinline.zip`. It exercises the interactions between `erasure-object.go`, `erasure-multipart.go`, and `erasure-metadata.go`.

Risks: many tests mutate global storage class or disk getter state; cleanup and reset discipline are important to avoid order sensitivity. Tests are heavier than pure unit tests and may be skipped/fragile on platform-specific filesystem behavior; `TestGetObjectWithOutdatedDisks` skips Windows. Some no-quorum tests compare wrapped errors with `errors.Is`, while others compare exact object errors, so error wrapping changes can affect tests unevenly.

Test signals: provides broad regression coverage for write/read/delete quorum boundaries, availability-optimized parity behavior, object version deletion semantics, MRF-worthy partial states, inline data compatibility, storage-class quorum computation, and read repair tolerance for outdated disks.
