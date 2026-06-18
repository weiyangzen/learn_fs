# sources/object-store/openstack-swift/swift/container/sharder.py

## Purpose

`swift/container/sharder.py` implements Swift's container sharding daemon. It scans local container DBs, audits root and shard containers, identifies containers or shard ranges that should split or shrink, creates shard containers, cleaves object rows from retiring DBs into destination shard DBs, moves misplaced objects, reports shard state to root containers, and records sharding progress and recon data.

The file combines pure shard-range algorithms with daemon orchestration. It extends `ContainerReplicator` so it can reuse ring traversal, local handoff selection, replication, reclaim, and DB deletion behavior while replacing the normal post-replicate hook with sharding-specific work.

## Important APIs, Types, and Functions

Module constants `CLEAVE_SUCCESS`, `CLEAVE_FAILED`, and `CLEAVE_EMPTY` classify a single shard-range cleave attempt.

Pure and mostly pure helpers include `sharding_enabled`, `make_shard_ranges`, `find_paths_with_gaps`, `_find_discontinuity`, `find_paths`, `rank_paths`, `find_overlapping_ranges`, sharding/shrinking candidate helpers, `find_compactible_shard_sequences`, `finalize_shrinking`, `process_compactible_shard_sequences`, `combine_shard_ranges`, and `update_own_shard_range_stats`.

`CleavingContext` persists progress for a retiring DB. It stores the DB-specific ref, namespace cursor, current max row, cleave-to row, previous cleave-to row, misplaced-done flag, cleaving-done flag, range counts, and accumulated replication time. It serializes to broker sharding sysmeta keys named `Context-<db id>`.

`ContainerSharderConf` loads and validates thresholds, batch sizes, timeouts, auto-shard settings, shrink/expand limits, rows per shard, and minimum shard size.

`ContainerSharder(ContainerSharderConf, ContainerReplicator)` is the daemon. Its methods cover stats and warnings, candidate detection, root/shard communication, broker auditing, object movement, cleaving, sharding completion, per-broker processing, shard-cycle orchestration, and entrypoint option handling.

## Control Flow

A sharder run begins in `run_once` or `run_forever`. Both call `_one_shard_cycle`, optionally with device and partition filters and command-line auto-shard override.

`_one_shard_cycle` resets stats, discovers local ring devices, populates `_local_device_ids`, builds datadir/partition iterators, opens each `ContainerBroker`, records candidate stats, calls `_process_broker` for sharding-enabled brokers, records progress, and reports stats.

`_process_broker` is the central state machine. It loads DB state, audits the container, moves misplaced objects, selects the auto-shard leader, bootstraps root sharding for large unsharded containers, transitions eligible DBs to `SHARDING`, scans and creates shard containers, replicates updated shard-range state, cleaves pending ranges, completes sharding when safe, identifies shrinking and further sharding candidates for sharded roots, and reports shard state back to roots for non-root containers.

The cleaving path is the highest-risk flow. `_cleave` loads a `CleavingContext`, first moves misplaced rows from the retiring DB, then iterates shard ranges after the context marker. It stops at gaps, unready states, failures, or `cleave_batch_size`. `_cleave_shard_broker` copies rows by name range and row id, syncs source DB sync points into the shard broker, updates shard range state and metadata, replicates the shard DB to enough peers, advances the context cursor, and persists the context. `_complete_sharding` activates cleaved ranges, marks the own range `SHARDED` or `SHRUNK`, deletes non-root own ranges when appropriate, and calls `broker.set_sharded_state()`.

The misplaced-object flow chooses source bounds based on DB state and cleaving cursor, partitions source rows across destination ranges from either the local root DB or a root GET, merges rows into local destination shard brokers, replicates each destination DB, and removes source rows only if replication is sufficiently successful and the source DB id did not change.

## State and Persistence Behavior

The sharder persists DB state transitions, own shard range state transitions, child/donor/acceptor/root shard ranges, object rows copied or removed during cleaving and misplaced movement, broker sync points copied to shard DBs, sharding sysmeta, serialized `CleavingContext` values, tombstone counts, and reported flags.

Shard container creation is persisted locally through `ContainerBroker.create_broker`, then replicated with `_replicate_object`. Remote creation and updates happen through direct container `PUT` calls with shard record type, sharding sysmeta, quoted root, storage-policy, and auto-create headers.

Recon state is written with `dump_recon_cache`, containing sharding stats, candidate summaries, progress data, and elapsed timing. Statsd metrics are emitted for many counters and timings.

`CleavingContext` is tied to the retiring DB id so a fresh DB epoch or replaced DB gets its own progress record. Completed or stale contexts are later cleared by `_audit_cleave_contexts`.

## Dependencies and Integration Points

Important dependencies include `ContainerReplicator`, `ContainerBroker`, backend state constants, `ShardRange`, `ShardRangeList`, timestamp helpers, `internal_client.InternalClient`, `direct_put_container`, ring utilities, statsd/recon helpers, and sharding-related request headers.

External integration points include container server shard GET/PUT APIs, container replicator behavior, proxy/object updater shard redirects, `swift-manage-shard-ranges`, and recon tooling.

## Risks and Edge Cases

Namespace correctness is the main risk. Gaps or overlaps in shard ranges can cause listing holes, duplicate listings, or misplaced object updates. The root audit checks overlaps and gaps, while shard audit only merges root-provided ranges when the combined set is safe.

Cleaving must be resumable and conservative. The context tracks both namespace cursor and row boundaries because rows can arrive while cleaving is in progress. If `max_row` changes after a full pass, `_complete_sharding` resets context so another pass cleaves new rows.

Replication quorum differs for new and existing shard containers. If the wrong quorum is used, the sharder may stall or remove source rows before enough destination replicas exist.

Shrinking changes bounds and donor states in the root, then asks donors to cleave into acceptors asynchronously. Incorrect acceptor expansion or donor deletion can create temporary listing gaps or permanent namespace loss.

Root and shard views can be stale during rolling upgrades and replication lag. `_merge_shard_ranges_from_root` is intentionally selective and refuses merges that introduce bad coverage.

Misplaced object cleanup only removes source rows after destination replication and DB-id stability checks.

Auto-shard leader selection depends on ring primary index 0. Handoffs and non-leaders can process already-enabled sharding but should not bootstrap new scans.

## Test Signals

High-value tests should cover pure range algorithms, candidate detection, `CleavingContext` persistence, config validation, root and shard audit warnings, root-merge selection, `yield_objects` ordering and markers, misplaced object movement, shard scanning and creation, cleaving success/failure/empty paths, replication quorum behavior, sharding completion for roots and shards, root update reporting, and full `_process_broker` state-machine paths for leader, non-leader, handoff, deleted, shrinking, and sharded-root cases.
