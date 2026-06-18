# sources/storage-engines/tikv/tests/failpoints/cases/test_split_region.rs

## Purpose
This large failpoint suite validates region split correctness across raftstore metadata, peer creation, snapshot interaction, split-check scheduling, pessimistic locks, leader election, raftstore-v2 split initialization, and PD heartbeat reporting. Its focus is preventing stale or duplicate peers, corrupted store metadata, wrong leader/read behavior, and lost split progress in race-heavy code paths.

## Important APIs, Types, And Functions
Important helper types are `PrevoteRangeFilter`, which records vote message ranges around split, `CollectSnapshotFilter`, which piles snapshot messages by source peer, and `TeeFilter`, which records outgoing raft messages. `gen_split_region` creates size-driven split scenarios. The suite uses `new_node_cluster`, `new_server_cluster`, `test_raftstore_v2`, `configure_for_merge`, `configure_for_snapshot`, `configure_for_request_snapshot`, PD `must_add_peer`/`must_remove_peer`/`must_merge`/`split_region`, `cluster.split_region`, `must_split`, `read_on_peer`, `TikvClient`, `PessimisticLockRequest`, `PrewriteRequest`, `SnapshotExt`, and raw access to store metas and local states. It uses many split failpoints, notably `before_set_region_on_peer_3`, `before_destroy_peer_on_peer_1003`, `apply_before_split_*`, `apply_after_split_*`, `is_generating_snapshot`, `region_split_skip_max_count`, `on_split_region_check_tick`, `on_handle_apply_*`, `before_check_snapshot_*`, `on_snap_msg_*`, `on_vote_msg_*`, `on_append_msg_*`, `on_heartbeat_msg_*`, `on_handle_apply_split_2_after_mem_check`, `on_split`, `after_split`, `txn_before_process_write`, `on_split_invalidate_locks`, `worker_gc_raft_log_flush`, `before_nofity_apply_res`, `begin_raft_poller`, `on_apply_batch_split`, `on_store_2_split_init_race_with_initial_message`, `tablet_trimmed_finished`, `fail_pre_propose_split`, and `test_pd_client::finish_region_heartbeat`.

## Control Flow
The opening tests create deliberately inconsistent timing: a peer is applying snapshot while a split inserts new region metadata, stale heartbeat triggers destroy, and a later split verifies meta remains consistent. Vote tests pause follower split apply and assert prevote/request-vote messages carry the new split range and are cached/responded after split completion. Snapshot-generation tests verify split checks pause when snapshot generation is in progress unless max skip count is reached.

The middle of the file focuses on duplicate or stale peer creation. It tests initialized peers with the same region ID, tombstoned peers, stale peers continuing to process snapshot/vote/append/heartbeat messages, uninitialized peers with same or different peer IDs, and destroy-after-memory-check ordering. These scenarios combine split, merge, peer remove/add, snapshot pauses, message isolation, and tombstone cleanup to ensure a split-created peer neither overwrites valid metadata nor resurrects removed data.

Other tests cover batching and statistics. `test_split_duplicated_batch` piles overlapping snapshots so an uninitialized peer and split peer can be fetched in one batch, ensuring ready results are mapped to the correct peer. Approximate size/key reporting tests assert split-check refreshes PD stats even when no split occurs. Split-check retry tests inject one failed pre-propose split and expect later size/key checks to complete.

The transaction section validates pessimistic lock safety during split. Concurrent lock/prewrite requests paused before processing must return `EpochNotMatch` when split invalidates in-memory locks or changes epoch, rather than writing locks to the wrong region or returning misleading `PessimisticLockNotFound`.

The final raftstore-v2 and election tests cover split during shutdown, split racing with conf change, split-init racing with initial messages without sending to store 0, slow split with tablet trim and dirty-data reset, new-region leadership after parent leader transfer, and pending peer reporting in PD heartbeats while a split peer has not applied yet.

## State And Persistence Behavior
The suite observes store metadata maps, region local states (`Normal`, tombstone/cleared), peer IDs and epochs, raft logs and log-GC responses, snapshot files/messages, in-memory pessimistic locks, approximate region size/keys, tablet dirty-data flags, PD heartbeat pending peers, and actual KV data by key range. Persistent behavior is validated by engine reads after split/merge/remove/readd operations and by ensuring destroyed regions are cleared while surviving ranges keep their data.

## Dependencies And Integration Points
This is a deep integration suite for raftstore peer FSM, apply FSM, split checker, PD scheduler, transaction lock manager, snapshot manager, raft transport filters, grpc `TikvClient`, tablet storage in raftstore-v2, and test macros that run selected cases against both raftstore implementations.

## Risks And Edge Cases
Covered risks include metadata corruption from concurrent destroy and split insert, dropped or misranged vote messages during slow split, duplicate initialized peers, stale uninitialized peers becoming valid after tombstone, split ready mapped to the wrong peer in a batch, epoch-unsafe pessimistic writes, async log-GC callbacks mutating a replacement peer, channel-full split result loss, shutdown races, messages to store 0 during split init, dirty-data never reset after tablet trim index mismatch, split retry starvation, and PD heartbeats missing pending peers.

## Test Signals
Signals include successful `must_put`/`must_get_equal` after each race, `must_get_none` for cleared stale ranges, expected `EpochNotMatch` errors, PD approximate stat changes, explicit leader identity assertions, pending peer checks in heartbeat callbacks, absence of messages to store 0, channel notifications from filters/failpoints, and no panic in previously corrupting races.
