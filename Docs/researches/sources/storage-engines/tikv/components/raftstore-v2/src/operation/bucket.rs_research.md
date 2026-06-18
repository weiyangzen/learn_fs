# sources/storage-engines/tikv/components/raftstore-v2/src/operation/bucket.rs

Purpose: Implements region bucket interactions for raftstore-v2: refreshing bucket metadata, propagating bucket refreshes to followers, updating read delegates, reporting bucket stats to PD, and triggering approximate bucket generation/split-check work.

Important APIs/types/functions: `Peer::on_refresh_region_buckets` updates local `region_buckets_info`, computes the next bucket version, notifies coprocessors, updates `StoreMeta` read progress, sends `ApplyTask::RefreshBucketStat`, and sends `MsgRefreshBuckets` raft extra messages to non-witness followers when leader. `Peer::on_msg_refresh_buckets` handles follower-side metadata updates. `report_region_buckets_pd`, `maybe_gen_approximate_buckets`, and `gen_bucket_range_for_update` connect bucket stats to PD and split-check. `PeerFsmDelegate::on_report_region_buckets_tick` and `on_refresh_region_buckets` provide message/tick entry points.

Control flow: A refresh request first rejects stale epochs, then updates bucket metadata only if bucket keys/ranges actually change. Leader refreshes are propagated to followers so they flush relevant memtables and update read progress. Periodic report ticks send deltas to the PD worker only when the peer is leader and has bucket stats.

State and persistence behavior: Bucket metadata is mostly in-memory in `region_buckets_info`, read delegates, and apply-side bucket stats. Apply tasks can maintain bucket counters in the apply FSM. The file does not write raft log entries itself; it sends raft extra messages and worker tasks.

Dependencies and integration points: It uses PD `BucketMeta`, raftstore bucket/range/read-progress utilities, coprocessor region change events, split-check tasks, PD worker tasks, `StoreContext`, and `PeerTick::ReportBuckets`.

Risks: Bucket version generation uses the raft term and warns if term exceeds `u32::MAX`, because versions could go backward. Follower refreshes do not update full bucket stats, only read progress metadata. `bucket_stat().unwrap()` assumes refresh produced bucket stats. Stale epoch checks are essential to avoid applying obsolete bucket layouts.

Test signals: No local tests. Integration should cover leader refresh propagation, stale epoch rejection, read delegate updates, PD report scheduling, witness exclusion, and bucket-range split-check generation.
