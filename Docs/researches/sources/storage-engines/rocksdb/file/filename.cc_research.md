# sources/storage-engines/rocksdb/file/filename.cc

## Purpose

`filename.cc` implements RocksDB's canonical file naming, filename parsing, and durable updates for key metadata files such as `CURRENT`, `IDENTITY`, manifests, options files, compaction-progress files, WALs, SSTs, blob files, and info logs. It is a central integration point between DB metadata, filesystem layout, and crash-safe state transitions.

## Important APIs, Types, and Functions

- Constants: `kCurrentFileName`, `kOptionsFileNamePrefix`, `kCompactionProgressFileNamePrefix`, `kTempFileNameSuffix`, plus internal extensions for `.sst`, `.ldb`, `.blob`, and `archive`.
- Name builders: `LogFileName`, `BlobFileName`, `ArchivalDirectory`, `ArchivedLogFileName`, `MakeTableFileName`, `TableFileName`, `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `OptionsFileName`, `TempOptionsFileName`, `CompactionProgressFileName`, `TempCompactionProgressFileName`, `MetaDatabaseName`, and `IdentityFileName`.
- Conversion helpers: `Rocks2LevelTableFileName`, `TableFileNameToNumber`, `FormatFileNumber`, `NormalizePath`.
- `InfoLogPrefix` and `GetInfoLogPrefix(...)` flatten DB absolute paths for info logs stored outside the DB directory.
- `ParseFileName(...)` classifies known RocksDB filenames into `FileType`, numeric id/timestamp, and optional WAL archival state.
- `SetCurrentFile(...)` writes a temp file containing the active manifest basename, renames it to `CURRENT`, and optionally fsyncs the containing directory.
- `SetIdentityFile(...)` writes or generates the DB identity, renames it into place, fsyncs the DB directory, and closes the directory if supported.
- `SyncManifest(...)` syncs a `WritableFileWriter` with the DB's fsync policy and records `MANIFEST_FILE_SYNC_MICROS`.
- `GetInfoLogFiles(...)` lists files in either `db_log_dir` or the DB path and filters using `ParseFileName`.

## Control Flow and State

Name builders format numbers with fixed six-digit file ids for numbered data/log/temp files and prefixes for manifest/options/progress files. `TableFileName` chooses a path by `path_id`, falling back to the last configured DB path if the id is out of range.

`ParseFileName` strips one leading slash, then checks exact metadata names, info-log prefixes, manifest/metadb/options/progress prefixes, and finally numeric files with suffixes. It intentionally uses `ConsumeDecimalNumber` rather than locale-sensitive conversion. Archived WALs are recognized by the `archive/` prefix and must have `.log` suffix; archived table/blob/temp files are rejected.

`SetCurrentFile` is the crash-sensitive path. It formats the manifest name, writes `dbname/<number>.dbtmp` with a trailing newline, injects test sync/kill points, renames the temp file to `CURRENT`, optionally fsyncs the directory, and best-effort deletes the temp file on failure. `SetIdentityFile` similarly writes temp `000000.dbtmp`, renames to `IDENTITY`, fsyncs the directory, tolerates `Close()` not-supported, and cleans up temp on failure.

Persistent state touched by this file is DB directory metadata: `CURRENT`, `IDENTITY`, option/progress/temp names, and file paths used by manifests, WALs, SSTs, blobs, and info logs. Pure name builders have no process state; `InfoLogPrefix` stores a fixed buffer and `Slice` view.

## Dependencies and Integration Points

The file depends on `file_util.h` for write option preparation, `writable_file_writer.h`, `FileSystem`, `Env`, sync-point testing hooks, stop watches, and string utilities. It is consumed broadly by DB open/recovery, manifest management, logging, compaction, backup/restore, and file deletion code. Test sync points named around `SetCurrentFile`, `SyncManifest`, and `FileMetaData` allow crash and upgrade tests to inject behavior.

## Risks and Edge Cases

- `ParseFileName` returns true after exact and prefix cases, but for malformed info-log prefixes that partially match and then do not satisfy old-log forms, callers should rely on initialized outputs only on recognized types.
- `TableFileNameToNumber` parses digits before the last dot and returns zero for malformed names; callers needing strict validation should use `ParseFileName`.
- `InfoLogPrefix` has a 260-byte fixed buffer and truncates by construction to leave room for `_LOG`; very long DB paths can collide after flattening/truncation.
- `SetCurrentFile` and `SetIdentityFile` rely on rename atomicity and directory fsync support; unsupported close is tolerated, but fsync errors propagate.
- Path construction mostly uses `/` directly even though `kFilePathSeparator` exists for normalization, so cross-platform semantics depend on RocksDB's path conventions and filesystem wrappers.

## Test Signals

Sync points and random kill hooks support crash-consistency tests around `CURRENT` updates and manifest sync. `prefetch_test.cc` uses a `FileMetaData` sync point to simulate missing file tail sizes during upgrade, indirectly relying on filename/manifest metadata behavior. Filename parsing and construction are typically covered by RocksDB filename tests outside this subset.
