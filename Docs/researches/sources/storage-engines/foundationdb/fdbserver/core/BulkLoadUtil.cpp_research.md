# sources/storage-engines/foundationdb/fdbserver/core/BulkLoadUtil.cpp

## Purpose
Implements bulk load file IO, transport, manifest parsing, metadata polling, and byte-sampling helpers. These utilities support storage-server fetch/load flows and bulk dump interoperability.

## Important APIs, Types, and Functions
- `readBulkFileBytes()`, `writeBulkFileBytes()`, and `copyBulkFile()` provide bounded async file IO with chunking and sync.
- `getBulkLoadTaskStateFromDataMove()` polls system metadata until a data-move record reaches a sufficient read version and contains `BulkLoadTaskState`.
- `doBytesSamplingOnDataFile()` scans a RocksDB SST file and writes a byte-sample SST when sampled keys exist.
- `clearFileFolder()` and `resetFileFolder()` manage local working directories.
- `bulkLoadTransportCP_impl()` and `bulkLoadTransportBlobstore_impl()` download remote file sets.
- `bulkLoadDownloadTaskFileSet()` and `bulkLoadDownloadTaskFileSets()` orchestrate downloads with retries and empty-range handling.
- Manifest helpers download job manifests, parse matching entries, and load task manifest metadata.

## Control Flow
File reads open uncached readonly files, reject oversized files, reserve output capacity, and append chunks after exact-size reads. Writes use atomic-create read/write mode, write chunks, truncate to final size, and sync. Download flows reset local folders, choose CP or blobstore transport, retry non-cancellation errors up to configured limits, and convert excessive failures to `bulkload_task_failed()` for data-distribution retry.

Manifest parsing reads a bounded file in 64 KiB chunks, preserves leftover partial lines, skips the header, and inserts entries whose ranges overlap the job range. Metadata loading downloads each referenced task manifest and adds it to a capped `BulkLoadManifestSet`.

## State and Persistence Behavior
Local filesystem state is aggressively reset for task folders. Remote state is read from CP paths or blobstore paths. FoundationDB state is read from `dataMoveKeyFor(dataMoveId)` using system-key and lock-aware options. No persistent database writes occur in this file.

## Dependencies and Integration Points
Depends on `BulkLoading`, NativeAPI, S3 client helpers, RocksDB checkpoint/SST utilities, server knobs, storage metrics, and Flow generic actors. It is used by storage-server bulk load/fetch paths and by bulk dump code for shared file operations.

## Risks and Edge Cases
The CP transport asserts a data file is present for single-file-set downloads, while multi-file-set downloads explicitly create markers for empty ranges. Blobstore downloads skip missing data files for empty ranges. Manifest and file size guards prevent unbounded memory use. Directory reset is a destructive local operation and must only target task-owned folders. Sampling retries indefinitely except cancellation, deleting partial sample files between attempts.

## Test Signals
No embedded tests here. Coverage should validate large chunked read/write, file-too-large errors, empty range handling, manifest chunk parsing with partial lines, download retry conversion to `bulkload_task_failed()`, and SST byte-sampling behavior.
