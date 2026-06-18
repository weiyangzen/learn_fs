# sources/storage-engines/tikv/src/server/raftkv/mod.rs

Purpose: implements the legacy `tikv_kv::Engine` adapter over raftstore. It converts storage reads/writes/admin operations into raft commands, maps raftstore responses into KV errors/results, handles async write event streams, exposes direct local-engine mutation for unsafe paths, and registers read-index lock checking for replica reads.

Important APIs/types/functions: `Error`; `CmdRes`; `RaftKv<E, S>`; `new_request_header`; `new_flashback_req`; `check_raft_cmd_response`; `async_write`; `async_snapshot`; `exec_admin`; `ReplicaReadLockChecker`.

Control flow: writes validate non-empty batches, inject failpoint errors, convert `Modify` values to raft requests, set one-pc/flashback/avoid-batch metadata, schedule txn-extra, and send raft commands with proposed/committed/applied callbacks. `WriteResFeed`/`WriteResSub` turn callbacks into `WriteEvent` streams. Snapshots build `Snap` raft requests, include read-index key ranges/start-ts, encode stale-read/flashback flags, and convert lock-conflict read-index responses into key-lock errors.

State/persistence: consensus writes persist through raftstore apply. `modify_on_kv_engine` bypasses raft and writes the local engine after wrapping data keys, rejecting SST ingest. `region_leaders` is an in-memory precheck; snapshot cache is released through router.

Dependencies/integration: raftstore routers/callbacks, `RegionSnapshot`, tracker metrics, concurrency manager, hybrid in-memory snapshots, txn-extra scheduling, and `RaftRouterWrap`. Risks include unsafe callback stream internals, undetermined callback-drop handling, duplicate-key debug panic, read-index parse unwraps, and dangerous local-engine bypass. Tests cover replica-read lock checker behavior.
