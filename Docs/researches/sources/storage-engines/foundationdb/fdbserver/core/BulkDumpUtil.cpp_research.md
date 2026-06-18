# sources/storage-engines/foundationdb/fdbserver/core/BulkDumpUtil.cpp

## Purpose
Provides storage-server bulk dump utilities for selecting dump workers, naming and writing dump files, uploading file sets, and marking dump ranges complete in system metadata.

## Important APIs, Types, and Functions
- `getSSBulkDumpTask()` chooses a target storage server from the first data-center group and records checksum servers from the remaining replicas.
- Filename/folder helpers generate versioned manifest, data SST, sample SST, and job/task folders.
- `getLocalRemoteFileSetSetting()` builds matching local and remote `BulkLoadFileSet`s.
- `writeKVSToSSTFile()` writes sorted key/value maps to RocksDB SST files.
- `dumpDataFileToLocalDirectory()` resets a local folder, writes data/sample SSTs, creates a manifest, and writes it atomically.
- `validateSourceDestinationFileSets()`, `uploadBulkDumpFileSet()`, and transport implementations move generated files by local copy or blobstore.
- `persistCompleteBulkDumpRange()` updates the `bulkDumpPrefix` key-range map after validating the task is still current.

## Control Flow
A dump task creates local files from raw range data, derives a manifest whose remote file set omits absent data/sample files, then uploads the local file set using the configured transport. Completion persistence reads the current bulk-dump key-range metadata in chunks, verifies job/task identity and submitted phase, writes the completed state over the task range, commits, and continues from the last returned range boundary.

## State and Persistence Behavior
Local disk state is reset before file generation or CP transport. Remote state is represented by uploaded manifest/data/sample paths. FoundationDB system state is updated through `krmGetRanges()` and `krmSetRange()` under `bulkDumpPrefix` with system and lock-aware transaction options.

## Dependencies and Integration Points
Depends on bulk loading/dumping metadata types, S3/blobstore helpers, RocksDB SST utilities, storage metrics types, and server knobs. It bridges bulk dump output into the same file-set and manifest structures consumed by bulk load.

## Risks and Edge Cases
Existing local output files are treated as retriable errors. Empty data ranges produce manifests without data or byte-sample file names. Source/destination validation enforces basename consistency and data/sample co-presence. Completion can throw `bulkdump_task_outdated()` if the task was cancelled, superseded, or already advanced.

## Test Signals
No embedded tests in this file. Useful signals are simulation tests for empty and non-empty dump ranges, CP and blobstore transports, stale task rejection, manifest correctness, and SST writer failure retries.
