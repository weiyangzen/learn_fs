# sources/storage-engines/rocksdb/tools/ldb_cmd_impl.h

## Purpose

`ldb_cmd_impl.h` declares the concrete `LDBCommand` subclasses implemented by `ldb_cmd.cc`. It is the internal command catalog for the RocksDB `ldb` utility: each class exposes a static command name, a constructor that consumes parsed parameters/options/flags, a `Help` method, and a `DoCommand` override. The header keeps command-specific state fields close to each declaration, making it the best map of command surface area and which commands open a DB, run read-only, operate offline, or need special options.

## Important APIs, types, and command classes

All classes derive from `LDBCommand` from `rocksdb/utilities/ldb_cmd.h`. The recurring public shape is `static std::string Name()`, a constructor taking command params/options/flags, `static void Help(std::string&)`, and `void DoCommand() override`. Several classes override `NoDBOpen`, `OverrideBaseOptions`, or `OverrideBaseCFOptions`.

The header declares command groups:

- Dump and inspection: `DBDumperCommand`, `InternalDumpCommand`, `DBFileDumperCommand`, `DBLiveFilesMetadataDumperCommand`, `ManifestDumpCommand`, `FileChecksumDumpCommand`, `WALDumperCommand`, `GetPropertyCommand`, `ListColumnFamiliesCommand`, `ListFileRangeDeletesCommand`, and `CompactionProgressDumpCommand`.
- Point and range access: `GetCommand`, `MultiGetCommand`, `GetEntityCommand`, `MultiGetEntityCommand`, `ScanCommand`, and `ApproxSizeCommand`.
- Writes and deletes: `PutCommand`, `PutEntityCommand`, `BatchPutCommand`, `DeleteCommand`, `SingleDeleteCommand`, and `DeleteRangeCommand`.
- DB and column-family administration: `CreateColumnFamilyCommand`, `DropColumnFamilyCommand`, `CompactorCommand`, `ReduceDBLevelsCommand`, `ChangeCompactionStyleCommand`, `CheckConsistencyCommand`, `CheckPointCommand`, and `RepairCommand`.
- Backup and file exchange: `BackupEngineCommand`, `BackupCommand`, `RestoreCommand`, `WriteExternalSstFilesCommand`, and `IngestExternalSstFilesCommand`.
- Offline or advanced metadata operations: `UpdateManifestCommand`, `UnsafeRemoveSstFileCommand`, `RemoteCompactionPrimaryCommand`, and `RemoteCompactionWorkerCommand`.

Important command-specific fields include key/range strings, max-key limits, count/stat flags, hex/input flags, checkpoint/backup paths, external SST options, ingest flags, level/compaction-style integers, live-file sort flags, WAL display flags, offline SST file numbers, and remote-compaction job directories.

## Control flow and class responsibilities

The header does not implement control flow itself, but it defines how `LDBCommand::SelectCommand` can instantiate every concrete command. Constructors are responsible for parsing and validating command-specific state; `DoCommand` performs the operation; `Help` contributes usage text.

`NoDBOpen()` communicates lifecycle expectations to the base runner. Most commands inherit the base behavior and open a DB before `DoCommand`. Offline or file-oriented commands override it:

- `ManifestDumpCommand`, `UpdateManifestCommand`, `FileChecksumDumpCommand`, `ListColumnFamiliesCommand`, `ReduceDBLevelsCommand`, `CheckConsistencyCommand`, `RepairCommand`, `RestoreCommand`, `UnsafeRemoveSstFileCommand`, `CompactionProgressDumpCommand`, `RemoteCompactionPrimaryCommand`, and `RemoteCompactionWorkerCommand` report no automatic DB open.
- `WALDumperCommand` returns `no_db_open_`, allowing optional DB open when `--db` is supplied for comparator-aware WAL formatting.
- Create/drop/external-SST commands explicitly return false or inherit opening behavior because they need a live DB handle.

Option overrides are declared where a command needs to alter base options before opening. `DBLoaderCommand`, `BatchPutCommand`, `PutCommand`, `PutEntityCommand`, `RepairCommand`, `WriteExternalSstFilesCommand`, and `IngestExternalSstFilesCommand` override `OverrideBaseOptions`, mostly to honor `create_if_missing`, bulk-load, or logging settings. `ReduceDBLevelsCommand` and `ChangeCompactionStyleCommand` override `OverrideBaseCFOptions` to force compaction/layout settings needed for their transformations.

## State and persistence behavior

The header's private fields reveal durable-effect boundaries. Read-only state includes scan ranges, dump ranges, count/stat flags, WAL formatting options, and metadata sort options. Mutating state includes keys and values for writes/deletes, column-family names to create/drop, external SST paths and ingest booleans, backup/restore directories, checkpoint directory, compaction level/style targets, and an SST file number for offline removal.

Persistence is ultimately performed in `ldb_cmd.cc`, but the declarations identify which commands can change DB state:

- Data writes/deletes: `DBLoaderCommand`, `PutCommand`, `PutEntityCommand`, `BatchPutCommand`, `DeleteCommand`, `SingleDeleteCommand`, and `DeleteRangeCommand`.
- Physical/layout changes: `CompactorCommand`, `ReduceDBLevelsCommand`, `ChangeCompactionStyleCommand`, `WriteExternalSstFilesCommand`, and `IngestExternalSstFilesCommand`.
- Metadata and lifecycle changes: `CreateColumnFamilyCommand`, `DropColumnFamilyCommand`, `CheckPointCommand`, `RepairCommand`, `BackupCommand`, `RestoreCommand`, `UpdateManifestCommand`, and `UnsafeRemoveSstFileCommand`.
- Cross-process compaction state: `RemoteCompactionPrimaryCommand` and `RemoteCompactionWorkerCommand` use a shared `job_dir_`.

The state fields are intentionally simple value types and raw command options; DB handles, column-family handle ownership, option loading, and env setup are inherited from `LDBCommand`.

## Dependencies and integration points

This header depends on `<map>`, `<string>`, `<utility>`, `<vector>`, and the public `rocksdb/utilities/ldb_cmd.h`. It is included by `ldb_cmd.cc`, and its class list must stay in sync with the string dispatch in `LDBCommand::SelectCommand`. The command names returned by `Name()` form the user-facing CLI vocabulary, so renames or additions must coordinate with help text, tests, docs, and any scripts that invoke `ldb`.

The declarations also expose integration with broader RocksDB features: TTL DB, transaction DB, backup engine, checkpoints, external SST ingestion, blob files, wide columns, MANIFEST/VersionSet tooling, compaction service, and column-family metadata. `BackupEngineCommand` is a protected base for `backup` and `restore`, sharing backup env/fs URIs, backup directory, thread count, logger, and env guard.

## Risks and edge cases

The main maintenance risk is drift between this command catalog and the implementation factory/help text. Adding a class here is insufficient unless `SelectCommand`, constructor validation, help output, and tests are updated. Conversely, stale declarations can leave unreferenced commands or inconsistent command names.

Commands with `NoDBOpen()` are not uniformly harmless: some are offline readers, while `UpdateManifestCommand`, `UnsafeRemoveSstFileCommand`, `RepairCommand`, and `RestoreCommand` can change persistent state without the normal live-DB open lifecycle. The header marks these lifecycle differences but cannot enforce operational safety by itself.

Several command states are sensitive to option semantics: range endpoints may be hex-decoded, TTL and timestamp flags affect iterator behavior, ingest flags have compatibility constraints, and level/compaction-style integers must match RocksDB enum values. The remote compaction commands rely only on `job_dir_` and `db_path_`, so concurrency and stale-file protections are implementation concerns rather than type-enforced guarantees.

The use of raw strings for wide-column `name:value` input, paths, and timestamps means validation lives entirely in constructors and `DoCommand` implementations. Tests should treat the header as the authoritative list of command surfaces that need argument validation coverage.

## Test signals

Header-level signals are mostly compile and dispatch signals: every declared `Name()` should be accepted by `LDBCommand::SelectCommand`, every `Help` should compile and mention required arguments, and every `NoDBOpen`/override choice should match command behavior. Tests should instantiate each command through parsed CLI arguments rather than direct constructors where possible, because this verifies the declared command names, option allowlists, and base lifecycle integration together.

Regression tests should cover new-command additions by checking dispatch, help text, missing required arguments, invalid command-specific options, and whether the command opens a DB automatically. For high-risk declarations such as `UnsafeRemoveSstFileCommand`, `UpdateManifestCommand`, restore, repair, external ingestion, and remote compaction, tests should verify both successful flows on isolated fixtures and refusal/failure behavior for invalid paths or unsafe option combinations.
