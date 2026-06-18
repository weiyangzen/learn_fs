# sources/storage-engines/tikv/cmd/tikv-ctl/src/cmd.rs

## Purpose
`cmd.rs` defines the complete `tikv-ctl` command-line schema using `StructOpt`. It maps global options and subcommands for inspecting, repairing, compacting, recovering, encrypting, and operating TiKV data and clusters.

## Important APIs, types, and functions
`Opt` holds global flags: PD address, log level/format, remote host, TLS paths, config/data-dir, RocksDB paranoid-check skip, deprecated `db`/`raftdb`, key conversion helpers (`--to-escaped`, `--to-hex`, `--decode`, `--encode`), and optional `Cmd`. `VERSION_INFO` lazily calls `tikv::tikv_version_info()` with `TIKV_BUILD_TIME`.

`Cmd` enumerates operational subcommands: raft log/region inspection, region size, MVCC/raw scans and prints, region diff, compaction, tombstone, MVCC recovery, unsafe recovery, recreate region, metrics, consistency check, bad region/SST inspection, config modification, snapshot metadata dump, cluster-wide compaction, region/range properties, split region, failpoint control, store/cluster IDs, file decryption, encryption metadata cleanup/dump, reset/flashback, raft-engine passthrough, readonly-remains reuse, compact-log-backup, and region read progress.

Nested enums are `RaftCmd`, `FailCmd`, `EncryptionMetaCmd`, and `UnsafeRecoverCmd`. The test module validates parser behavior for `compact-log-backup` flags such as default `gcp_v2_enable`, explicit false, `cal_shift_ts`, and omitting `--until` when a replication-status prefix is provided.

## Control flow
There is no executor logic here; control flow is declarative parser construction. `StructOpt` derives generate clap parsing with conflicts, required-unless rules, defaults, aliases, value delimiters, possible values, and external subcommand capture. Later executor modules match on `Opt.cmd` and run the actual operations.

## State and persistence behavior
This file does not persist state directly, but many parsed commands authorize state-changing operations: writing RocksDB pages/metadata, tombstoning regions, removing failed stores, dropping unapplied raft logs, compaction, config modification, decryption output, encryption metadata cleanup, reset/flashback, and backup-log compaction. Parser constraints are therefore an important safety boundary.

## Dependencies and integration points
It depends on `clap`, `structopt`, `compact_log_backup::ShardConfig`, `engine_traits` constants/types, `raft_engine::ReadableSize`, and `tikv` version reporting. It integrates with the rest of `tikv-ctl` by providing the typed command contract consumed by executor code and tests.

## Risks and edge cases
Parser-level safety is only as strong as declared conflicts and requirements. Several destructive commands include `all-regions`, `force`, or recovery semantics; accidental defaults or missing confirmations can be dangerous downstream. `External(Vec<String>)` captures unknown subcommands and may defer errors. Some deprecated fields remain with validators that always error, preserving visible compatibility while blocking use. Value delimiters and `possible_values` protect some fields but not all path/key inputs.

## Test signals
Existing tests cover a subset of `compact-log-backup`. Additional useful tests include command conflict rules, deprecated flag errors, required-unless behavior for unsafe recovery/recover MVCC/diff, value delimiter parsing, `possible_values` rejection, key conversion flag conflicts, external subcommand handling, and help/version output.
