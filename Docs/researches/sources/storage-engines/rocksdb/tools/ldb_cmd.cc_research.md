# sources/storage-engines/rocksdb/tools/ldb_cmd.cc

## Purpose

`ldb_cmd.cc` implements the command factory, shared option/opening machinery, and concrete command bodies for RocksDB's `ldb` utility. It covers direct key/value reads and writes, scans, dumps of DB/WAL/SST/MANIFEST/blob state, column-family management, compaction/repair/checkpoint/backup/restore workflows, external SST generation and ingestion, manifest mutation utilities, and a local-file remote-compaction demonstration path.

The file is the execution side of the public command declarations in `rocksdb/utilities/ldb_cmd.h` and the local declarations in `tools/ldb_cmd_impl.h`. It turns parsed CLI arguments into `LDBCommand` subclasses, prepares `Options` and column-family descriptors, opens the correct DB flavor, executes the selected command, prints user-facing output, and records failures in `LDBCommandExecuteResult`.

## Important APIs, types, and functions

The central APIs are `LDBCommand::InitFromCmdLineArgs`, `ParseSingleParam`, `SelectCommand`, `Run`, `OpenDB`, `CloseDB`, `PrepareOptions`, `OverrideBaseOptions`, `OverrideBaseCFOptions`, `ValidateCmdLineOptions`, `MaybePopulateReadTimestamp`, and the shared formatting helpers `HexToString`, `StringToHex`, `PrintKeyValue`, and `PrintKeyValueOrWideColumns`.

Command classes implemented here include:

- Read/query commands: `GetCommand`, `MultiGetCommand`, `GetEntityCommand`, `MultiGetEntityCommand`, `ScanCommand`, `ApproxSizeCommand`, `DBQuerierCommand`, `GetPropertyCommand`, and `ListFileRangeDeletesCommand`.
- Mutation commands: `PutCommand`, `PutEntityCommand`, `BatchPutCommand`, `DeleteCommand`, `SingleDeleteCommand`, `DeleteRangeCommand`, `CreateColumnFamilyCommand`, `DropColumnFamilyCommand`, `WriteExternalSstFilesCommand`, and `IngestExternalSstFilesCommand`.
- Dump and inspection commands: `DBDumperCommand`, `InternalDumpCommand`, `DBFileDumperCommand`, `DBLiveFilesMetadataDumperCommand`, `ManifestDumpCommand`, `FileChecksumDumpCommand`, `WALDumperCommand`, and `CompactionProgressDumpCommand`.
- Maintenance commands: `CompactorCommand`, `ReduceDBLevelsCommand`, `ChangeCompactionStyleCommand`, `CheckConsistencyCommand`, `CheckPointCommand`, `RepairCommand`, `BackupCommand`, `RestoreCommand`, `UnsafeRemoveSstFileCommand`, `UpdateManifestCommand`, `RemoteCompactionPrimaryCommand`, and `RemoteCompactionWorkerCommand`.

Important local helpers include `WALFileIterator`, `DumpWalFiles`, `DumpWalFile`, `DumpSstFile`, `DumpBlobFile`, `DumpManifestFile`, `DumpCompactionProgressFile`, `GetLiveFilesChecksumInfoFromVersionSet`, `EncodeUserProvidedTimestamp`, `AtomicWriteStringToFile`, `PollForFile`, and `LocalFileCompactionService`. WAL rendering relies on `InMemoryHandler`, a `WriteBatch::Handler` that decodes puts, entities, merges, deletes, range deletes, prepare/commit/rollback records, timestamps, and column-family ids.

The file depends heavily on RocksDB internals: `DBImpl`, `VersionSet`, `VersionEdit`, `OfflineManifestWriter`, `WriteBatchInternal`, internal key formatting, blob indexes, wide-column serialization, log readers, file-name parsing, SST file dumping, backup/checkpoint utilities, TTL DB, TransactionDB, and experimental manifest update APIs.

## Control flow

Top-level control starts with command-line parsing. `ParseSingleParam` splits `--name=value` options, `--flag` flags, and positional command tokens. `InitFromCmdLineArgs` assigns `cmd` and `cmd_params`, calls `SelectCommand`, then injects default `Options`, `LDBOptions`, and optional column-family descriptors into the selected command.

`SelectCommand` is a long string-to-subclass factory. Each subclass constructor validates its positional arguments, command-specific options, and flags, and builds its allowed option list from `BuildCmdLineOptions`. Common options include DB path, env and filesystem URIs, column family, secondary/follower paths, compression/table/blob options, TTL/transaction flags, hex formatting, create-if-missing, and option-file loading controls.

`Run` is the command lifecycle:

- Create or resolve the configured `Env` from `env_uri`/`fs_uri`.
- Open the DB unless the command reports `NoDBOpen()`.
- Continue to `DoCommand()` even after some open failures for dump-style commands that may operate on standalone files.
- Convert an untouched execution state to success.
- Close the DB and column-family handles after command execution.

`OpenDB` calls `PrepareOptions`, then selects one DB open mode: `TransactionDB::Open`, `DBWithTTL::Open`, normal `DB::Open`, `DB::OpenForReadOnly`, `DB::OpenAsSecondary`, or `DB::OpenAsFollower`. It rejects unsupported combinations such as TTL plus transaction mode, TransactionDB plus read-only/secondary/follower mode, and simultaneous secondary and leader paths. When multiple column families are opened it stores handles in `cf_handles_` and comparators in `ucmps_`, then verifies the requested `--column_family` exists.

`PrepareOptions` optionally loads the latest OPTIONS file, registers custom compression, adjusts missing WAL directories, populates column-family descriptors from OPTIONS or MANIFEST, installs a default string-append merge operator when none is configured, and applies CLI overrides. Overrides can adjust table factory, Bloom filter, block size, uniform CV threshold, compression and blob settings, prefix extractor, auto compaction, write buffer sizes, target file size, consistency checks, and `create_if_missing`.

Individual command control flow is direct:

- Read commands set `ReadOptions`, optionally attach a user-defined read timestamp, call point/multi-get/entity APIs, then print either values, wide columns, not-found messages, or per-key errors.
- Scan and dump commands create iterators with total-order seek, enforce start/end/max-key limits, handle TTL timestamp filtering, optionally print write unix time, and format plain values, wide columns, blob indexes, or counts.
- Write commands decode optional hex input and issue one RocksDB write API call or one `WriteBatch`.
- File dump commands dispatch by RocksDB filename type to WAL, SST, MANIFEST, or blob-file dumpers.
- Maintenance commands call RocksDB utility APIs such as `CompactRange`, `RepairDB`, `Checkpoint::CreateCheckpoint`, backup engine creation/restoration, external-file ingestion, offline manifest editing, and manifest temperature updates.

## State and persistence behavior

This file controls both transient process state and durable RocksDB state. Transient command state lives in `LDBCommand` fields such as `db_`, `db_ttl_`, `db_txn_`, `cf_handles_`, `ucmps_`, `options_`, `config_options_`, `option_map_`, `flags_`, `read_timestamp_`, and `exec_state_`. `CloseDB` deletes opened column-family handles, closes the DB, resets ownership, and clears TTL/transaction raw pointers.

Durable effects vary by command:

- `put`, `put_entity`, `batchput`, `delete`, `singledelete`, and `deleterange` write user records or tombstones to the selected column family.
- `load` streams `key ==> value` lines from stdin into the DB, can disable WAL, can prepare for bulk load, and can compact after load.
- `compact`, `reduce_levels`, and `change_compaction_style` rewrite SST layout through manual compaction and, for level reduction, may update manifest metadata after compaction.
- `create_column_family` and `drop_column_family` update DB metadata.
- `checkpoint` creates a physical checkpoint directory.
- `repair` rewrites/reconstructs DB metadata through `RepairDB`.
- `backup` creates a backup in `backup_dir`; `restore` restores the latest backup into the DB path.
- `write_extern_sst` writes an external SST file from stdin without ingesting it; `ingest_extern_sst` links or copies that file into the DB according to `IngestExternalFileOptions`.
- `unsafe_remove_sst_file` edits the manifest offline to delete an SST reference and is explicitly unsafe for live DBs.
- `update_manifest` runs an experimental manifest-file-state update and is also unsafe for live DBs.
- `remote_compaction_primary` and `remote_compaction_worker` coordinate through `job_dir/input.bin`, `job_dir/result.bin`, and `job_dir/output`, using atomic temp-file rename for handoff.

Read-only and dump commands still open DBs in read-only mode where possible, but some `NoDBOpen()` commands call `PrepareOptions` and operate on files or manifests directly. `DBDumperCommand` intentionally supports both `--db` database dumping and `--path` standalone file dumping.

## Dependencies and integration points

The implementation is integrated with the CLI wrapper that calls `LDBCommand::InitFromCmdLineArgs`, with command declarations in `tools/ldb_cmd_impl.h`, and with the public `rocksdb/utilities/ldb_cmd.h` command base. It uses RocksDB core APIs (`DB`, `ColumnFamilyHandle`, `Iterator`, `WriteBatch`, `SstFileWriter`, `BackupEngine`, `Checkpoint`, `TransactionDB`, `DBWithTTL`) and internal APIs (`VersionSet`, `OfflineManifestWriter`, `DBImpl`, log reader, filename parser, internal-key utilities, wide-column helpers, blob index decoder).

Output formatting is part of the tool contract: `DELIM` separates key/value dump lines, `--hex`, `--key_hex`, and `--value_hex` affect input decoding and output encoding, and timestamp-enabled comparators affect both key validation and display. The WAL dumper integrates with comparator metadata from opened column-family handles so WAL keys with user timestamps can be rendered correctly.

External integrations include custom Env/FileSystem URIs for DB and backup locations, stdin for `load` and external SST writing, filesystem path parsing for DB files, `/dev/stdin` optimization where available, stderr logging through `StderrLogger`, and `TEST_SYNC_POINT_CALLBACK` in range-delete listing for tests.

## Risks and edge cases

The highest-risk behaviors are commands that mutate durable metadata without normal DB ownership: `unsafe_remove_sst_file` and `update_manifest` explicitly must not run on live DBs. `repair`, `restore`, level reduction, compaction-style conversion, external ingestion, and drop-column-family are also high-impact operations that need clear operator intent and backups.

Option parsing has a few sharp edges. Boolean parsing throws on values other than `true` or `false`; many constructors parse numeric options with `stoi` and may fail early; some parse failures only set `exec_state_`, so command code must consistently stop on failed state. Hex decoding throws string literals on invalid input. `PutEntityCommand` splits wide columns on `:` and requires exactly two split parts, so names or values containing additional colons are rejected. `DBQuerierCommand` tokenizes on single spaces and directly indexes `tokens[1]` in several branches, so malformed interactive input needs careful coverage.

Open-mode compatibility is subtle. TTL does not support multiple column families here; TransactionDB is rejected with TTL, read-only, secondary, and follower modes; option-file loading is disabled by default for TTL. Commands marked `NoDBOpen()` sometimes call `PrepareOptions` or `OpenDB` manually, so lifecycle assumptions are command-specific.

Timestamp support is intentionally strict. `MaybePopulateReadTimestamp` rejects missing or empty `--read_timestamp` when the comparator has user-defined timestamps, and rejects a timestamp argument for comparators without timestamps. WAL dumping verifies recorded timestamp sizes against comparator timestamp sizes when DB comparators are available and fails on mismatch.

Formatting and dump behavior can be misleading if the DB is not opened with all relevant column families: WAL keys from unknown CF ids fall back to hex. `DBDumperCommand` chooses standalone file behavior by parsed file name, not content probing. `DumpSstFile` reads without checksum verification. `DBFileDumperCommand` contains a potential null/invalid ownership issue around `Checkpoint::Create` because the raw `Checkpoint*` is not wrapped or deleted after use, and if creation failed the next dereference would be unsafe.

The local-file remote compaction path is a demonstration-style integration with fixed filenames, a single scheduled job assertion, and a 120-second polling timeout. It requires two processes sharing the same `job_dir`; stale files or concurrent users can confuse scheduling.

## Test signals

Useful test signals include CLI construction/validation tests for every command name and option list; open-mode tests for read-only, TTL, TransactionDB, secondary/follower, multiple column families, missing column family, and OPTIONS-file loading; golden-output tests for `dump`, `idump`, `scan`, `get`, `multi_get`, wide-column entity output, WAL output, manifest JSON/text output, checksum output, and live-file metadata sorting.

Persistence tests should exercise `put`/`get`, `batchput`, deletes, range deletes, load/dump round trips with hex and plaintext, external SST write plus ingest, checkpoint reopen, backup/restore reopen, repair on damaged fixtures, level reduction on multi-level fixtures, and compaction-style conversion. Risk-focused tests should cover invalid hex and boolean values, user timestamp mismatch/missing cases, WAL timestamp-size mismatch, unknown WAL column-family ids, `--path` file-type dispatch, malformed stdin load lines, and the explicit live-DB hazards for offline manifest commands.
