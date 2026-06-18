# sources/storage-engines/tikv/components/batch-system/benches/batch-system.rs

## Purpose
Criterion microbenchmarks for whole-system batch polling under load, imbalance, and fairness scenarios.

## APIs, Types, And Functions
Uses `batch_system::test_runner` to construct simple `Runner` FSMs. `end_hook` sends a completion signal through `Message::Callback`. Benchmarks are `bench_spawn_many`, `bench_imbalance`, and `bench_fairness`, grouped as `fair` and `load`.

## Control Flow
Each benchmark creates a control FSM, system/router, starts worker threads, registers normal FSM mailboxes, sends messages, then waits for callback acknowledgements before each iteration completes. The fairness benchmark additionally runs a background producer against hot FSMs while measuring whether quick tasks on other FSMs still complete.

## State And Persistence
State is transient benchmark state: registered mailboxes, atomic flags/counters, and mpsc completion channels. No persistent output is written except Criterion benchmark data outside this source file's direct concern.

## Dependencies And Integration Points
Exercises `create_system`, `BasicMailbox`, `Router::register`, `Router::send`, and shutdown behavior. It depends on the test runner model rather than production raftstore FSMs, making it a focused performance harness.

## Risks And Test Signals
These benches signal the scheduler's expected properties: high fan-out throughput, spreading hot FSMs, and avoiding starvation. They do not assert correctness but are useful regressions for scheduling algorithm or channel implementation changes.
