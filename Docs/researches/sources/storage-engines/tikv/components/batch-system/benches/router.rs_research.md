# sources/storage-engines/tikv/components/batch-system/benches/router.rs

## Purpose
Criterion microbenchmark for the hot `Router::send` path to a registered normal FSM.

## APIs, Types, And Functions
`bench_send` constructs a test batch system, registers a single `BasicMailbox`, and repeatedly sends `Message::Loop(0)` to address `1`.

## Control Flow
Setup starts the system, registers one normal FSM, then Criterion repeatedly invokes `router.send`. Shutdown occurs after the benchmark closure is registered.

## State And Persistence
Transient system state includes the control FSM, normal mailbox, scheduler channels, and worker threads. No persistent data is written.

## Dependencies And Integration Points
Focuses on router lookup, mailbox send, and FSM notification. Uses the same test runner helper as other benchmarks.

## Risks And Test Signals
Useful for detecting overhead in the most common routing operation. It does not measure end-to-end handler processing or full-channel cases.
