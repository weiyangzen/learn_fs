# sources/object-store/openstack-swift/swift/obj/replicator.py

## Purpose
Implements the object replicator daemon for replicated storage policies. It compares local and remote suffix hashes, transfers out-of-sync suffixes using rsync or ssync, reverts handoff partitions to their primary nodes, removes handoff data after successful sync, and writes replication health statistics to the recon cache. Unlike the EC reconstructor, this daemon handles whole replicated object partitions and does not rebuild fragments.

## Important APIs, Types, And Functions
`DEFAULT_RSYNC_TIMEOUT` defines the default subprocess timeout for rsync. `_do_listdir(partition, replication_cycle)` spreads expensive suffix-directory list operations over ten replication cycles.

`Stats` is the daemon’s recon/stat aggregation type. It tracks attempted jobs, failures, hash matches, removals, rsync/ssync attempts, successful target devices, suffix counts, suffix hashes, suffix syncs, and nested failure counts by remote IP/device. It supports `from_recon()`, `to_recon()`, addition, and `add_failure_stats()`.

`ObjectReplicator` owns configuration, ring/device discovery, transfer methods, job construction, pass execution, and recon updates. Key methods include `get_worker_args()`, `is_healthy()`, `get_local_devices()`, `sync()`, `load_object_ring()`, `_rsync()`, `rsync()`, `ssync()`, `revert()`, `delete_partition()`, `delete_handoff_objs()`, `update()`, `build_replication_jobs()`, `collect_jobs()`, `replicate()`, `update_recon()`, `aggregate_recon_update()`, `run_once()`, and `run_forever()`.

## Control Flow
`run_once()` or `run_forever()` zeroes stats and calls `replicate()`. A replication pass advances `replication_cycle`, starts a heartbeat, collects jobs, checks ring changes, validates device mounts, and dispatches each job into a green pool. Jobs with `delete=True` are handoff reverts; other jobs are primary partition updates.

`collect_jobs()` iterates replication policies, skips policies under `next_part_power`, honors policy overrides, loads rings, and delegates to `build_replication_jobs()`. `build_replication_jobs()` finds local ring devices by IP/port, validates drives through `check_drive()`, cleans stale tmp files, creates missing object data directories, lists partitions, ignores auditor status files, and creates a job containing the partition path, local device, object path, remote primary nodes, delete flag, policy, partition, and local region. A partition becomes a handoff job when the local device is not one of the partition’s primary nodes.

`update()` handles primary partitions. It computes local suffix hashes, shuffles target primary nodes, and chains extra handoff nodes if needed. For each target region not already successfully synced, it sends a backend `REPLICATE` request, handles 507 unmounted responses by trying another node, unpickles remote hashes, computes suffix differences, recalculates local hashes for those suffixes, and invokes the configured `sync_method` (`rsync` by default, `ssync` if configured). Successful cross-region syncs suppress duplicate syncs to the same remote region during the pass.

`revert()` handles handoff partitions under a replication partition lock to avoid cross-replication races with incoming SSYNC. It lists suffix directories, syncs each remote primary, optionally passes `remote_check_objs` for same-region ssync optimizations, and decides whether to delete the handoff partition. With `handoff_delete` set, a configured number of successful syncs is enough; otherwise all intended syncs must succeed. If using ssync and cross-region syncs reported object sets, it deletes only objects known to be present remotely; otherwise it removes the whole partition. Empty handoff partitions are also removed.

The rsync path builds an rsync command over existing suffix directories, uses xattrs, excludes temporary files, optionally compresses cross-region transfers, then sends a backend `REPLICATE` notification for the synced suffixes unless the job is a failed delete. `_rsync()` bounds subprocess runtime, kills long-running children, hands stubborn child reaping to a background greenlet, limits error log lines if configured, and logs transfer output according to settings.

## State And Persistence
Persistent effects include rsync/ssync writes to remote object servers, local handoff partition deletion via `shutil.rmtree`, per-object handoff cleanup via `delete_handoff_objs()`, stale tmp cleanup through `unlink_older_than()`, and creation of missing object data directories. Replicated object contents, metadata, tombstones, and suffix hash files are owned by the DiskFile layer.

In-memory pass state includes `stats_for_dev`, `partition_times`, `replication_cycle`, `all_devs_info`, `handoffs_remaining`, current ring mtimes, and child rsync processes awaiting reaping. Recon state is persisted in `RECON_OBJECT_FILE`; single-process runs write aggregate `replication_stats`, while multiprocess workers write `object_replication_per_disk` entries and the parent aggregates them only when every current local device has reported.

## Dependencies And Integration Points
The daemon depends on Swift ring placement, `POLICIES` filtered to `REPL_POLICY`, `DiskFileRouter`, backend object-server `REPLICATE`, optional `ssync_sender.Sender`, external `rsync`, `check_drive()`, `is_local_device()`, recon-cache helpers, and eventlet/tpool concurrency. It is launched through `run_daemon(ObjectReplicator, ...)` and accepts CLI overrides for devices, partitions, and policies.

It integrates directly with `obj/server.py` for remote suffix hash retrieval and post-rsync hash invalidation, and with `obj/ssync_sender.py` when configured to use ssync instead of rsync. Handoff cleanup relies on consistent object hashes and storage-directory layout from the DiskFile implementation.

## Risks And Edge Cases
Deletion is the primary operational risk. Handoff partitions or objects are removed only after configured success criteria, but aggressive `handoff_delete` values can trade durability margin for faster rebalance. `delete_handoff_objs()` intentionally removes object hash directories and prunes suffix directories, so object-set calculation from ssync must remain correct.

Other sensitive areas include unmounted drives, rsync subprocess hangs, ring changes mid-pass, `next_part_power` policies, invalid partition files, cross-region deduplication, and multiprocess recon aggregation with stale per-disk entries. The rsync path shells out and depends on remote module interpolation and xattr support; the ssync path depends on protocol compatibility with receivers. Suffix hashes are recalculated before transfer to reduce false positives, but races with live writes are expected and resolved by later passes.

## Test Signals
Focused tests should cover `Stats` aggregation and recon serialization, `_do_listdir()` cycle spreading, rsync argument construction and timeout handling, `update()` suffix-delta/recalc behavior, 507 fallback to handoffs, `revert()` deletion criteria for default and `handoff_delete` modes, `delete_handoff_objs()` suffix pruning, worker device distribution, ring-change aborts, and recon-cache aggregation. Integration tests should exercise both rsync-style REPLICATE notifications and ssync-based handoff cleanup. The local checkout does not include upstream tests, so these signals are inferred from the daemon’s public behavior.
