# sources/storage-engines/tikv/components/batch-system/src/test_runner.rs

## Purpose
Provides a simple FSM and handler implementation for batch-system tests and benchmarks.

## APIs, Types, And Functions
`Message` has `Loop`, `Callback`, and `Resource` variants and implements `ResourceMetered`. `Runner` is a test FSM with receiver, mailbox, optional sender, result accumulator, and priority. `HandleMetrics` tracks handler calls. `Handler` consumes up to 16 messages per invocation and implements `PollHandler<Runner, Runner>`. `Builder` constructs handlers with shared metrics and pause counters.

## Control Flow
Tests create `Runner::new` sender/FSM pairs, wrap them in mailboxes, and register them. Handler loops perform synthetic CPU work, execute callbacks, or consume resource messages. `handle_control` and `handle_normal` both process messages and report progress zero so the batch system releases the FSM until new messages arrive.

## State And Persistence
All state is transient. Shared metrics are stored in `Arc<Mutex<HandleMetrics>>`, pause counts in `Arc<AtomicUsize>`, and priority in each runner.

## Dependencies And Integration Points
Integrates with `ResourceController`, TiKV mpsc, batch traits, and optional `derive_more` arithmetic derives. It is feature-gated by the crate's `test-runner` feature.

## Risks And Test Signals
Because tests and benches depend on this helper, changes can mask or create false failures in batch-system validation. Its resource message support is key to testing resource-control ordering.
