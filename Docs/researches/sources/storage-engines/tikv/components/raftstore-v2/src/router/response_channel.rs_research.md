# sources/storage-engines/tikv/components/raftstore-v2/src/router/response_channel.rs

Purpose: this file implements reusable async response channels for raftstore-v2 read/write/debug commands, including optional proposed/committed events and cancellation semantics.

Important APIs/types/functions: `EventCore<Res>` stores a two-bit-per-event atomic state, optional result, optional before-set callback, waker, and tracker. `BaseChannel`/`BaseSubscriber` form generic result channels. `CmdResChannel`, `CmdResSubscriber`, `CmdResChannelBuilder`, `CmdResStream`, and `CmdResEvent` support raft write responses and proposed/committed notifications. `AnyResChannel`, `QueryResChannel`, `DebugInfoChannel`, `ReadResponse`, and `QueryResult` specialize payloads. Test-export `FlushChannel` exists behind a feature gate.

Control flow: producers call `notify_event` for proposed/committed milestones and `set_result` once for final payload; dropping a channel calls `cancel`. Subscribers poll `WaitEvent` or `WaitResult`, registering an `AtomicWaker` and setting subscribed bits via CAS. `CmdResStream` yields proposed, committed, then finished events according to the channel's event mask.

State and persistence: all state is in memory. The event atomic reserves event 0 for payload and 31 for cancellation. Trackers carry read or write latency metadata through callback trait implementations.

Dependencies/integration: implements raftstore callback traits `ErrorCallback`, `WriteCallback`, and `ReadCallback`; integrates with tracker TLS, raft command protobufs, transaction extra op, and region meta debug responses.

Risks: `UnsafeCell` plus atomics require strict single-result/single-consumer assumptions. The source includes a FIXME that `set_result` may need a stronger ordering barrier to prevent result write reordering before event publication. `take_result`/`result` cannot safely race each other despite `Sync` impl.

Test signals: local tests cover cancellation, channel result delivery, query responses, before-set callback mutation, and `CmdResStream` event sequencing.
