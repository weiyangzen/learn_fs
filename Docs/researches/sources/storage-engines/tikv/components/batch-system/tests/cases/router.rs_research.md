# sources/storage-engines/tikv/components/batch-system/tests/cases/router.rs

## Purpose
Tests router send semantics, capacity behavior, close/shutdown cleanup, and mailbox leak tracing.

## APIs, Types, And Functions
Helper messages include `counter_closure`, `noop`, and an intentionally unreachable callback. Tests are `test_basic` and `test_router_trace`.

## Control Flow
`test_basic` verifies missing mailbox errors, registers a mailbox from a control callback, tests normal and force sends, fills a channel to observe `Full`, unblocks and flushes callbacks, closes the mailbox, and then shuts down the system. `test_router_trace` registers 10 runners, holds mailbox handles, closes router entries, and checks `state_cnt` only drops after handles are released.

## State And Persistence
State is in-memory test routers, mailboxes, channels, and atomic counters. Drop notifications are observed by receiver disconnection.

## Dependencies And Integration Points
Exercises `Router`, `BasicMailbox`, mpsc capacity behavior, `BatchSystem::shutdown`, and `RouterTrace` state accounting.

## Risks And Test Signals
Strongly validates edge cases around disconnected/full sends and resource release. It also documents expected behavior that external mailbox handles can keep FSM state alive after router close.
