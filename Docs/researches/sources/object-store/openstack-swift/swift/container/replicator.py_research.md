# sources/object-store/openstack-swift/swift/container/replicator.py

## Purpose

`swift/container/replicator.py` specializes Swift's generic database replicator for container databases. It replicates normal container DB rows, sharding metadata, sync-store state, and reconciler queue entries. The file is also the server-side RPC extension used by the container server's `REPLICATE` endpoint.

The core responsibilities are:

- Keep local container DBs synchronized with peer replicas using `swift.common.db_replicator`.
- Exchange container shard range rows in addition to ordinary DB replication metadata.
- Stop object-row replication once a container has started sharding, so cleaving rather than old replication paths moves rows to shard containers.
- Detect objects recorded under the wrong storage policy and enqueue those rows into local reconciler containers under `.misplaced_objects`.
- Keep the local `sync_containers` symlink store in step when container metadata changes or DBs are deleted.
- Create, replicate, and eventually clean up local reconciler container DBs produced during a replication pass.

## Important APIs, Types, and Functions

`check_merge_own_shard_range(shards, broker, logger, source)` filters incoming shard range dictionaries before merging. It specifically protects a broker whose own shard range has an epoch from being overwritten by a remote copy of the same own shard range that lacks an epoch. This is a compatibility workaround for historical data and logs a warning when it ignores such a remote row.

`ContainerReplicator` extends `db_replicator.Replicator` with container-specific constants: `server_type = 'container'`, `brokerclass = ContainerBroker`, `datadir = DATADIR`, and default port `6201`.

Key `ContainerReplicator` methods include sync-arg extension, sync-response policy/timestamp repair, all-range shard-range replication, sharding-aware replication-mode selection, reconciler DB creation and feeding, sync-store refresh, DB cleanup, and reconciler replication at the end of `run_once`.

`ContainerReplicatorRpc` extends `db_replicator.ReplicatorRpc` for container replication RPCs. It parses optional newer sync args, repairs policy index before returning local replication info, aborts rsync-then-merge if the local DB began sharding, preserves shard ranges across rsync, and exposes `merge_shard_ranges` and `get_shard_ranges`.

`main()` wires the daemon entry point, including once-mode device and partition overrides.

## Control Flow

A normal once pass starts in `run_once`: it constructs `reconciler_containers`, `reconciler_cleanups`, and a `ContainerSyncStore`, then calls the generic DB replicator scan. For each DB, generic replication calls into the container overrides.

When a peer responds to sync, `_handle_sync_response` decodes remote info, updates local storage policy and timestamps when remote values are newer or more correct, fetches remote shard ranges if the peer advertises `shard_max_row`, and delegates remaining response handling to the generic replicator.

Replication mode selection is sharding-aware. `_choose_replication_mode` first tries to push shard ranges if the peer understands `shard_max_row`. If `broker.sharding_initiated()` is true, the method refuses normal object replication, records a deferred stat, and returns only the shard-range replication result. This is important because object movement must happen via sharder cleaving.

After normal replication, `_post_replicate_hook` refreshes the sync-store symlink and handles misplaced rows. Multi-policy containers call `dump_to_reconciler`, which batches rows from `broker.get_misplaced_since` by reconciler container name, translates each row to a queue entry, and merges those items into local reconciler brokers. The reconciler sync point advances only if a majority of peer replication responses were successful.

At the end of the pass, `replicate_reconcilers` pushes generated reconciler containers to their proper nodes, then disables the cleanup bypass and deletes local cleanup candidates.

Incoming `REPLICATE` requests hit `ContainerReplicatorRpc` through `server.py`. The sync handshake is policy-aware, rsync merges preserve shard ranges, and explicit shard-range RPCs move sharding metadata without requiring a full DB transfer.

## State and Persistence Behavior

The main persistent state is in container SQLite DBs managed by `ContainerBroker`: replication info, timestamps, policy index, shard ranges, reconciler sync point, misplaced rows, and normal object rows when generic replication is still allowed.

Reconciler queue state is persisted as container DBs under `MISPLACED_OBJECTS_ACCOUNT`. `get_reconciler_broker` creates a local broker on a local device for the reconciler container derived from the object's timestamp. These DBs are cached for the duration of `run_once`.

Sync-store state is persisted outside SQLite as symlinks in each device's `sync_containers` tree. Replication refreshes the symlink when metadata changes and removes it before deleting a DB.

Shard range replication currently sends all shard ranges every cycle rather than maintaining shard-range sync points.

## Dependencies and Integration Points

This module depends on `swift.common.db_replicator`, `ContainerBroker`, `swift.container.reconciler`, `ContainerSyncStore`, `POLICIES`, timestamp helpers, and utility functions such as `majority_size`, `get_db_files`, and `node_to_string`.

Runtime integration points include the container server `REPLICATE` endpoint, the container sharder, the object/container reconciler pipeline, account update reporting fields, and container sync discovery through `ContainerSyncStore`.

## Risks and Edge Cases

Shard-range epoch handling is subtle. If `check_merge_own_shard_range` is bypassed or altered incorrectly, an old remote own shard range without epoch can erase important local epoch state and confuse sharding progress.

The refusal to replicate object rows after sharding starts is intentional but high impact. A false positive in `broker.sharding_initiated()` would defer normal replication; a false negative would allow object rows to replicate while cleaving is expected to own movement.

Reconciler sync point advancement depends on majority replication. Bugs here can either duplicate reconciler work or lose misplaced-object repairs.

`find_local_handoff_for_part` must find a local device. If ring/local-device metadata is stale, reconciler broker creation can fail or pick a fallback device with zero weight.

The shard-range RPC sends all shard ranges. Very large shard-range tables may make replication heavier than normal object-row diffs.

`delete_db` has different behavior for reconciler DBs during `run_once`; mistakes in that lifecycle can leave local reconciler DBs around or delete them before they are replicated.

## Test Signals

Useful tests should cover epoch-preserving shard-range merge filtering, sync-arg compatibility, sharding-aware object replication deferral, policy/timestamp repair on sync response, shard-range RPC responses, reconciler batching and sync-point advancement, sync-store updates, DB deletion behavior, and reconciler replication/cleanup ordering.
