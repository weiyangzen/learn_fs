## sources/storage-engines/tikv/components/server/src/common.rs

Purpose: shared startup/runtime utilities for TiKV-like servers: config validation, filesystem locks, encryption/IO setup, PD connection, quota tuning, engine migration, metrics, compaction pressure, stop abstraction, hybrid engine construction, and disk usage checks.

Important APIs/types/functions: `TikvServerCore`, `EnginesResourceInfo`, `ConfiguredRaftEngine`, `EngineMetricsManager`, `DiskUsageChecker`, `Stop`, `build_hybrid_engine`, `check_system_config`, and lock helpers.

Control flow: startup calls `init_config`, `check_conflict_addr`, `init_fs`, `init_yatp`, `init_encryption`, `init_io_utility`, `init_flow_receiver`, and `connect_to_pd_cluster`. Background tasks tune quota from process CPU usage, flush engine/IO metrics, update compaction pressure, and classify disk status. `ConfiguredRaftEngine` specializations migrate raft logs between RocksDB raftdb and raft-log-engine when the persisted state machine says a switch is needed.

State/persistence: manages data-dir locks, conflict-address lock files, reserved disk placeholder files, encryption key manager, flow channels, worker stop list, raft data migration, metrics reset timers, and moving averages of compaction pressure.

Dependencies/integration: ties together tikv config/controller, encryption, Rocks/raft engines, file_system IO limiter, PD client, security, raftstore, in-memory engine, prometheus/yatp, and system quota/disk APIs.

Risks: many failures are fatal by design; disk reservation and migration code mutate on-disk layout; compaction tuning assumes CF ordering matches `DATA_CFS`; disk status depends on mount separation heuristics and configured thresholds.

Test signals: unit tests cover `DiskUsageChecker` states under failpointed disk stats and `EnginesResourceInfo::update` selecting latest tablets and clearing caches.
