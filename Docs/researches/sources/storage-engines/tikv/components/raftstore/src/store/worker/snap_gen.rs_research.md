# sources/storage-engines/tikv/components/raftstore/src/store/worker/snap_gen.rs

Purpose: this worker generates raft snapshots asynchronously from KV snapshots. It offloads snapshot building to a YATP future pool, notifies the requester through a synchronous channel, and nudges raftstore so generated snapshots can be sent.

Important APIs and types:
- `SNAP_GENERATOR_MAX_POOL_SIZE` caps the intended generator pool size.
- `Task<S>::Gen` carries region id, last applied term/state, a KV snapshot, cancellation flag, notifier, load-balance marker, and destination store id.
- `SnapGenContext<EK, R>` captures the engine, snapshot manager, router, and generation start timestamp for the async job.
- `Runner<EK, R, T>` owns the engine, `SnapManager`, router, optional PD client, future pool, and a `tiflash_stores` cache.

Control flow:
- `Runner::run` handles only `Task::Gen`. It decides whether multi-file snapshots are allowed based on the destination store. Non-TiFlash targets can receive multi-file snapshots; TiFlash or unknown/error cases disable that optimization.
- Store label lookup is cached by `to_store_id`; the PD lookup treats lookup failure as TiFlash-like to avoid sending unsupported snapshot formats.
- The runner increments snapshot metrics, builds a `SnapGenContext`, records queue wait time, and spawns `ctx.handle_gen` into the future pool.
- `handle_gen` checks cancellation before doing I/O, sets the I/O type to load-balance or replication, calls `generate_snap`, updates success/failure/abort counters, and records duration.
- `generate_snap` calls `store::do_snapshot`, optionally triggers failpoints, tries to send the resulting raft snapshot to the notifier, then sends `CasualMessage::SnapshotGenerated` to the region router.

State and persistence behavior:
- This file does not persist raft metadata directly. Persistence is delegated to `store::do_snapshot` and `SnapManager`, which create snapshot files under the snapshot manager directory.
- `UnixSecs::now()` is captured at scheduling time and passed into snapshot creation, likely for snapshot metadata/file lifecycle.
- Cancellation is cooperative and checked before snapshot generation starts; there is no mid-generation cancellation in this file.

Dependencies and integration points:
- Depends on `engine_traits::KvEngine` for the source snapshot type.
- Uses `pd_client::PdClient` to inspect target store labels and avoid unsupported multi-file snapshots for TiFlash.
- Uses `file_system::WithIoType` for I/O classification.
- Integrates with raftstore via `CasualRouter` and `CasualMessage::SnapshotGenerated`; callers in apply/peer paths receive the snapshot through `SyncSender<RaftSnapshot>`.

Risks and edge cases:
- If the notifier channel is closed, generation is considered successful and only logged, because leadership may have changed and heartbeat can retry.
- Future-pool spawn failure increments failure metrics but does not notify the requester directly.
- PD label lookup failure disables multi-file snapshots for that target, a safe but possibly slower fallback.
- The `tiflash_stores` cache has no explicit invalidation in this file; store label changes may not be observed until runner restart.

Test signals:
- This file has no local test module. It is indirectly covered by `region.rs` snapshot apply tests, which schedule `SnapGenTask::Gen`, receive generated snapshots, copy them into receiving snapshots, and then apply them.
