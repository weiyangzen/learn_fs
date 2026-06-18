# sources/storage-engines/tikv/components/raftstore/src/router.rs

Purpose: Provides raftstore routing traits and adapters for raft messages, proposals, casual/significant peer messages, store messages, local reads, coprocessor callbacks, and CDC leadership/change observer hooks.

Important APIs and types: `RaftStoreRouter<EK>` composes `StoreRouter`, `ProposalRouter`, `CasualRouter`, and `SignificantRouter`, adding methods such as `send_raft_msg`, `broadcast_normal`, `send_command`, `report_unreachable`, `report_snapshot_status`, and store reachability helpers. `ReadContext` carries optional thread read id and timestamp. `LocalReadRouter` abstracts local read execution and snapshot-cache release. `RaftStoreBlackHole` is a no-op router for tests or disabled paths. `ServerRaftStoreRouter` wraps a `RaftRouter` plus `LocalReader`. `CdcHandle` and `CdcRaftRouter` expose CDC/PiTR scheduling through significant messages.

Control flow: `send_command_impl` extracts the region id, wraps the request/callback as `RaftCommand`, attaches extra options, and sends through a proposal router. `handle_send_error` maps full queues to `Transport(Full)` and disconnected proposal channels to `RegionNotFound(region_id)`. `ServerRaftStoreRouter` delegates every routing trait to the underlying raft router or local reader. The `StoreHandle` impl on `RaftRouter` converts coprocessor events into `CasualMessage` variants, logging failures instead of surfacing them.

State and persistence: The router owns no durable state. It controls message delivery and therefore indirectly affects raft persistence and proposal progress. Local reads may use cached snapshots via `LocalReader`, with explicit cache release.

Dependencies and integration points: It depends on engine traits, raft snapshot status, raft command protobufs, raftstore FSM router traits, transport router traits, coprocessor `StoreHandle`, local reader, and CDC change observers. It is a central integration layer used by server frontends, coprocessors, snapshot transport feedback, and CDC/PiTR.

Risks: Several methods intentionally log-and-drop coprocessor feedback on routing failure, which protects background tasks but can delay split-size, hash, bucket, or compaction-decline updates. The black-hole router can hide behavior if accidentally used outside tests or disabled components. Mapping disconnected proposal send to `RegionNotFound` is pragmatic but may obscure shutdown versus actual missing-region causes.

Test signals: No tests are in this file. Its behavior is indirectly covered by raftstore routing, local-read, CDC, and coprocessor tests.
