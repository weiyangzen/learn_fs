# sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_router.rs

Purpose: Routes each peer's async write messages to a store write worker while preserving per-peer ordering and optionally rescheduling hot peers across workers once previous writes have persisted.

Important APIs and types: `WriteRouterContext` abstracts access to `WriteSenders`, raftstore `Config`, and local raft metrics. `WriteRouter<EK, ER>` tracks the current writer id, retry time, pending reschedule target, last unpersisted ready number, buffered messages, and last resource-control priority. `SharedSenders` wraps the sender vector stored in a `VersionTrack`. `WriteSenders` caches tracked senders and holds a shared `io_reschedule_concurrent_count`.

Control flow: `send_write_msg` resets priority when there are no pending writes, calls `should_send`, and either sends immediately or buffers the message. `should_send` randomly chooses a worker when there is no previous unpersisted ready, avoids rescheduling when disabled or before the hot-spot duration, chooses a different worker as `next_writer_id`, and uses an atomic concurrent-count limit before buffering. `check_new_persisted` completes a reschedule once the persisted ready number reaches `last_unpersisted`, swaps to the new writer, decrements gauges/counters, and drains buffered messages to the new worker. `send` consumes resource quota, tries priority send, and falls back to blocking send while recording write-block wait.

State and persistence: The router itself is in-memory, per peer. Its key state invariant is that buffered messages are not sent to a new worker until earlier writes are durable, preserving sequential handling for a peer. It also carries `last_msg_priority` so resource-control scheduling can maintain per-peer order.

Dependencies and integration points: It depends on `resource_control::channel::Sender`, raftstore `Config`, `PollContext`, write metrics, async `WriteMsg`, and `VersionTrack` configuration updates. `StoreWriters` in `write.rs` owns the shared sender set that `WriteSenders` tracks.

Risks: Random writer choice means tests and behavior must tolerate no-op reschedule attempts when the same worker is selected. If persisted notifications stall, buffered messages remain pending and gauges stay elevated. `SharedSenders` uses a manual `unsafe impl Sync` based on access discipline; violating that discipline could expose sender internals to races. Pool size is min-capped against local cached senders to handle config updates before poller refresh.

Test signals: `test_write_router_no_schedule` verifies disabled rescheduling keeps all messages on the original worker. `test_write_router_schedule` verifies reschedule start, buffering, no completion before the persisted threshold, drain after threshold, and retry behavior when the concurrent reschedule limit is saturated.
