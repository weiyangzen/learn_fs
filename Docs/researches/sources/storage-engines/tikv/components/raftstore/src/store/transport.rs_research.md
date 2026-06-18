# sources/storage-engines/tikv/components/raftstore/src/store/transport.rs

## Purpose

Defines raftstore transport and router traits plus concrete adapters for the production `RaftRouter` and test/std channels. It gives store, peer, proposal, casual, significant, and async-read code a small common API while normalizing full/disconnected channel errors into raftstore `Error`/`DiscardReason` values.

## Important APIs, Types, And Functions

`Transport` is the network-facing raft message sender abstraction with `send`, `set_store_allowlist`, `need_flush`, and `flush`. `CasualRouter<EK>` routes best-effort peer messages to a region. `SignificantRouter<EK>` routes forced significant messages to a region, using `EK::Snapshot` in the message type. `ProposalRouter<S>` sends raft commands carrying an engine snapshot. `StoreRouter<EK>` routes messages to the store FSM. Implementations exist for `RaftRouter<EK, ER>`, `&Mutex<T>` wrappers, `mpsc::SyncSender` test channels, and `mpsc::Sender<StoreMsg<EK>>`. `AsyncReadNotifier` is implemented for `RaftRouter` to send fetched raft logs back as a significant peer message.

## Control Flow

Production casual sends call `RaftRouter.router.send(region_id, PeerMsg::CasualMessage(...))`; full mailboxes become `Error::Transport(DiscardReason::Full)`, while disconnected mailboxes become `Error::RegionNotFound(region_id)`. Significant sends call `force_send` so they bypass normal bounded-send behavior; if delivery fails, the code logs at warn for ignorable send failures and error otherwise, then returns `RegionNotFound`. Store routing delegates to `send_control` and maps full/disconnected control mailbox failures to transport discard reasons. Proposal routing delegates to `send_raft_command` and preserves `TrySendError<RaftCommand<S>>`.

The std-channel implementations are mainly adapters for tests or small components: `SyncSender<(u64, CasualMessage<EK>)>` uses `try_send`, `SyncSender<RaftCommand<S>>` maps std `TrySendError` into crossbeam `TrySendError`, and `mpsc::Sender<StoreMsg<EK>>` treats send failure as disconnected. `notify_logs_fetched` ignores missing regions because async-read log fetches can race with region removal; `notify_snapshot_generated` is unreachable for this router implementation.

## State And Persistence Behavior

This file owns no persistent state. Its behavior is defined by the underlying mailbox/router state and channel capacity. The distinction between casual bounded send and significant force send is the important runtime state interaction: significant messages are intended for control paths where dropping on full mailboxes would violate higher-level progress or cleanup expectations.

## Dependencies And Integration Points

Depends on `engine_traits::{KvEngine, RaftEngine, Snapshot}`, kvproto `RaftMessage`, raftstore message enums (`CasualMessage`, `SignificantMsg`, `StoreMsg`, `RaftCommand`, `PeerMsg`), `RaftRouter`, async read notification types, and `crossbeam`/std channel errors. It is re-exported by `store/mod.rs` and used by snapshot generation workers, read workers, PD workers, backup snapshot handling, unsafe recovery, peer FSM helpers, and tests that substitute channel routers.

## Risks

The error mapping is semantically important. Casual peer send treats disconnection as region-not-found, while store send treats it as transport disconnected; changing this can alter retry/drop behavior. Significant messages use force send, so overuse can pressure mailboxes but is required for recovery, snapshot, and control events. The `&Mutex<T>` adapters lock synchronously and can propagate poisoning panics through `unwrap`. `notify_snapshot_generated` being unreachable assumes no caller uses `RaftRouter` as a snapshot-generation notifier; a new caller would panic.

## Test Signals

There are no local tests, but many raftstore worker and FSM tests instantiate mock routers or std-channel implementations of these traits. Useful regression signals include full-channel handling, disconnected-region handling, significant message delivery for unsafe recovery and snapshot backup, proposal routing through read workers, and async-read `RaftlogFetched` notifications being ignored when the region disappears.
