## sources/storage-engines/tikv/components/server/src/server.rs

Purpose: orchestrates full TiKV server startup, service registration, background tasks, pause/resume, graceful shutdown, and stop sequencing.

Important APIs/types/functions: public `run_tikv`; internal `run_impl`; `TikvServer`, `TikvEngines`, `Servers`, and methods `init`, `init_raw_engines`, `init_engines`, `init_servers`, `register_services`, `init_metrics_flusher`, `init_storage_stats_task`, `run_server`, `run_status_server`, `pause`, `resume`, `graceful_shutdown`, and `stop`.

Control flow: `run_tikv` logs quotas, performs pre-start checks, dispatches by API version and raft engine choice, initializes `TikvServer`, sets memory high-water handling, checks locks/filesystems, initializes engines, servers, services, metrics, cgroup/storage/max-ts tasks, starts grpc/status servers, and then handles service events until shutdown. `init_servers` constructs flow control, GC, CDC, resolved-ts, read pools, resource metering recorder/reporter/sinks, storage, raft server, coprocessor, backup, split, import, and debug infrastructure before starting raft and workers.

State/persistence: owns engine handles, store metadata, workers, config controller, PD client, security manager, snapshot manager, resource manager, quota limiter, raft system/router, memory/statistics state, lock files, and stop list. It opens and mutates persistent RocksDB/raft engines, snapshot/import directories, and runtime lock files.

Dependencies/integration: this is the integration point for almost every component in the manifest: PD, raftstore, storage, grpc services, security, resource metering, CDC, backup, import SST, diagnostics/debug, in-memory engine, quota/resource control, and signal handling.

Risks: startup is order-sensitive and many errors are fatal; background tasks assume initialized fields via `unwrap`; resource metering must be started before storage request tagging; graceful shutdown depends on PD scheduler and leader eviction completing before timeout; stop ordering must prevent engines/workers from outliving dependencies.

Test signals: inline test covers `EnginesResourceInfo` compaction-pending behavior. Most server behavior is integration-tested elsewhere; this file’s code relies heavily on subsystem tests.
