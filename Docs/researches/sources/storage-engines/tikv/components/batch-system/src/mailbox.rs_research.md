# sources/storage-engines/tikv/components/batch-system/src/mailbox.rs

## Purpose
Implements message mailboxes that pair a channel with atomic FSM ownership. Mailboxes deliver messages and notify schedulers when an idle FSM should be polled.

## APIs, Types, And Functions
`BasicMailbox<Owner>` stores a `LooseBoundedSender` and `Arc<FsmState<Owner>>`. It exposes `new`, `len`, `is_empty`, `force_send`, and `try_send`; crate-private methods handle connection status, ownership release/take, and close. `Mailbox<Owner, Scheduler>` wraps a basic mailbox with a scheduler for ergonomic `force_send` and `try_send`.

## Control Flow
Both send methods first charge message resource usage through the scheduler, enqueue the message, and then call `FsmState::notify`. `force_send` bypasses channel capacity; `try_send` respects it. Closing the mailbox closes the sender and clears the FSM state.

## State And Persistence
All state is in memory. Cloned mailboxes share the sender and FSM state. The mailbox is responsible for temporarily transferring FSM ownership to a poller and later accepting it back through `release`.

## Dependencies And Integration Points
Uses TiKV loose bounded mpsc channels, crossbeam send errors, `FsmState`, and `FsmScheduler`. Routers store `BasicMailbox` values and return high-level `Mailbox` handles to callers.

## Risks And Test Signals
Resource leaks, duplicate scheduling, or dropped idle FSMs are key risks. Router tests exercise full, disconnected, force-send, close, and drop behavior; batch tests exercise normal message scheduling through mailboxes.
