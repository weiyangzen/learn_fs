# sources/storage-engines/tikv/etc/config-template.toml

## Purpose
Provides the human-readable TiKV configuration template and documentation for operational tuning. Almost every setting is commented, giving default values, units, deployment caveats, and performance tradeoffs for logs, memory, thread pools, storage, Raft, RocksDB, security, backup, pessimistic transactions, and GC.

## Important APIs, Types, and Functions
The template covers top-level logging and memory limits; `[quota]`; `[log]` and `[log.file]`; `[memory]`; read pools; `[resource-control]`; `[server]`; `[storage]`, block cache, flow control, and IO rate limit; `[pd]`; `[raftstore]`; coprocessor sections; `[rocksdb]` with default/write/lock CF and Titan options; `[raftdb]`; `[raft-engine]`; TLS and encryption settings; import/backup/log-backup; pessimistic transactions; and GC.

## Control Flow
This file is consumed as a config template rather than executed. Operators uncomment and tune entries, and TiKV's configuration loader applies them at startup or, for documented dynamic settings, through runtime configuration mechanisms.

## State and Persistence Behavior
It does not persist state itself, but many settings control persistent layout and compatibility: storage engine choice, data directories, WAL directories, Raft Engine format/recycle behavior, RocksDB table format/checksum/compression, Titan enablement/fallback, encryption metadata format, and backup/log-backup behavior.

## Dependencies and Integration Points
Integrates with TiKV server startup, RocksDB/RaftDB/Raft Engine, PD connectivity, backup systems, TLS certificate provisioning, KMS/file encryption providers, Prometheus-observed resource limits, and operational tooling that generates final TiKV configs.

## Risks
Some options are not safely mutable after cluster creation, especially storage engine and Titan-related behavior. Misconfigured memory, block cache, flow control, compaction, WAL, or Raft log settings can cause OOM, write stalls, data unavailability, or disk exhaustion. Security sections can disable TLS or choose weak master-key handling if copied uncritically.

## Test Signals
Validate generated configs with TiKV config-check tooling/startup dry runs. Exercise representative workloads after changing block cache, flow control, RocksDB, Raft, or quota settings. Check downgrade/upgrade compatibility for format-version, encryption dictionary log, Titan, and Raft Engine options.
