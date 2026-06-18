# sources/storage-engines/rocksdb/file/filename.h

## Purpose

`filename.h` declares the filename contract for RocksDB database files. It defines the public internal interface for constructing, parsing, and committing file names used by WALs, SSTs, blobs, manifests, options snapshots, compaction-progress files, info logs, lock files, metadata databases, `CURRENT`, and `IDENTITY`.

## Important APIs, Types, and Functions

- `kFilePathSeparator` abstracts the platform separator for path normalization.
- WAL/blob/table builders include `LogFileName`, `BlobFileName`, `ArchivedLogFileName`, `MakeTableFileName`, `Rocks2LevelTableFileName`, `TableFileNameToNumber`, `TableFileName`, and `FormatFileNumber`.
- DB metadata builders include `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `OptionsFileName`, `TempOptionsFileName`, `CompactionProgressFileName`, `TempCompactionProgressFileName`, `MetaDatabaseName`, and `IdentityFileName`.
- `InfoLogPrefix` stores a fixed buffer and a `Slice` naming prefix for regular or external log directories.
- `ParseFileName` has an overload that accepts `info_log_name_prefix` and one that skips info-log files.
- Mutating APIs include `SetCurrentFile`, `SetIdentityFile`, and `SyncManifest`.
- `GetInfoLogFiles` enumerates recognized info logs in a parent directory.
- `NormalizePath` collapses repeated separators while preserving UNC path prefix shape.

## Control Flow and State

The header itself has no implementation beyond declarations and constants. It defines which filename forms the implementation must produce and parse. The stateful operations it declares update persisted DB metadata (`CURRENT`, `IDENTITY`, manifest sync) through `FileSystem`, `Env`, `WritableFileWriter`, and directory handles.

## Dependencies and Integration Points

The declarations depend on DB path options, platform helpers, `FileSystem`, public `Options`, `Slice`, `Status`, and transaction-log file types. DB open/recovery, version-set/manifest code, WAL management, logging, and table-file placement all consume these APIs, making this header part of RocksDB's storage layout ABI.

## Risks and Edge Cases

- Any change to generated names or parse rules can affect recovery, backup compatibility, log discovery, and external tools.
- The overload that skips info logs is useful for callers that enumerate DB-owned numbered files but can surprise callers expecting `LOG` recognition.
- `SetCurrentFile` requires a valid directory handle when the caller wants directory fsync; omitting it trades durability for caller-managed sync semantics.
- The path-normalization contract is intentionally narrow and should not be treated as full canonicalization.

## Test Signals

Most tests are indirect: DB reopen, recovery, flush/compaction, manifest sync, and log listing all depend on these declarations. The corresponding implementation contains sync points used by crash/upgrade tests.
