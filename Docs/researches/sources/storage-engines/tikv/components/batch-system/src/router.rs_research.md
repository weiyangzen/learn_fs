# sources/storage-engines/tikv/components/batch-system/src/router.rs

## Purpose
Routes messages to normal FSM mailboxes by address and to the single control FSM. It also owns registration, shutdown, broadcast, and lightweight leak tracing.

## APIs, Types, And Functions
`RouterTrace` reports alive and leaked mailbox counts. `Router<N,C,Ns,Cs>` stores a `DashMap<u64, BasicMailbox<N>>`, a control mailbox, normal/control schedulers, shared state count, and shutdown flag. Important methods include `register`, `send_and_register`, `register_all`, `mailbox`, `control_mailbox`, `try_send`, `send`, `force_send`, `send_control`, `force_send_control`, `broadcast_normal`, `broadcast_shutdown`, `close`, `alive_cnt`, and `trace`.

## Control Flow
Normal sends look up a mailbox, try to enqueue through it, convert full/disconnected/missing cases into either send errors or returned messages, and increment channel-full metrics. `force_send` retries with mailbox `force_send` if bounded send reports full. Shutdown closes all normal mailboxes, clears the map, closes control, and asks both schedulers to shut down. `close` removes one mailbox and shrinks the map when excess capacity grows.

## State And Persistence
Router state is in-memory and shared by clones. Mailbox map entries own normal FSM states. The shutdown flag alters `force_send` handling so disconnected sends after shutdown can be treated as success.

## Dependencies And Integration Points
Integrates `DashMap`, mailbox types, scheduler traits, TiKV `Either`, and batch-system metrics. Higher-level raftstore/apply systems use region IDs or similar addresses as router keys.

## Risks And Test Signals
Risks include stale mailbox handles, capacity-full behavior, replacement closing old mailboxes, and state-count leaks. Tests validate missing sends, force send, full channel handling, close/drop resource release, shutdown, and `RouterTrace` accounting.
