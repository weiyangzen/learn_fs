# sources/storage-engines/rocksdb/db/filename_test.cc

## Purpose
`filename_test.cc` validates RocksDB file-name parsing, construction, info-log naming, and path normalization. It ensures durable file naming conventions remain compatible for WALs, SSTs, MANIFESTs, CURRENT, LOCK, temp files, metadata DB files, and info logs in default or separate log directories.

## Important APIs, Types, and Functions
The test fixture is `FileNameTest`. It exercises `ParseFileName`, `InfoLogPrefix`, `InfoLogFileName`, `OldInfoLogFileName`, `CurrentFileName`, `LockFileName`, `LogFileName`, `TableFileName`, `DescriptorFileName`, `TempFileName`, `MetaDatabaseName`, and `NormalizePath`. It checks returned `FileType` values such as `kWalFile`, `kTableFile`, `kCurrentFile`, `kDBLockFile`, `kDescriptorFile`, `kMetaDatabase`, `kInfoLogFile`, and `kTempFile`.

## Control Flow
`Parse` loops over successful cases for three modes: default info-log directory, different info-log directory with a generated prefix, and no log-dir prefix checking. It verifies file number and type, including the maximum `uint64_t` WAL number. It then loops over malformed names and overflowed numbers that must fail.

`InfoLogFileName` computes an absolute DB path, verifies normal `LOG`/`LOG.old.N` naming under the DB directory, and verifies prefixed log names under a separate info-log directory. `Construction` generates each canonical file name, strips the directory prefix, parses it, and checks type/number. It also checks `TableFileName` path selection from one or multiple `DbPath` entries. `NormalizePath` checks duplicate separator collapse while preserving important UNC/server-prefix behavior.

## State and Persistence Behavior
The file does not mutate DB state, but it protects persisted naming contracts. These names are how RocksDB discovers WALs, table files, descriptors, lock files, and logs on restart or cleanup. Incorrect parsing can cause recovery to ignore live files or treat unrelated files as DB files. Incorrect construction can place table files in the wrong DB path or make generated names unparsable.

## Dependencies and Integration Points
The test depends on `file/filename.h`, `db/dbformat.h`, `Env::GetAbsolutePath`, `DbPath`, path separator constants, and the RocksDB test harness. It integrates with DB open/recovery, MANIFEST management, WAL discovery, obsolete-file cleanup, multi-path table placement, and info-log rotation.

## Risks
Filename parsing must reject partial prefixes, wrong suffixes, and numeric overflows. Info-log parsing is sensitive because separate log directories use DB-path-derived prefixes, so tests distinguish default, different-dir, and unchecked modes. Path normalization must collapse redundant separators without destroying root or UNC semantics.

## Test Signals
The test provides table-driven positive and negative parse coverage, round-trip construction coverage, separate log-dir naming checks, and platform-aware separator normalization. The `main` function installs the stack trace handler and runs the RocksDB test harness.
