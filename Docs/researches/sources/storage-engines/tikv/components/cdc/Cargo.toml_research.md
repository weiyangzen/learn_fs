# sources/storage-engines/tikv/components/cdc/Cargo.toml

## Purpose
Defines the TiKV `cdc` crate and its broad dependency/feature surface for change-data-capture service code.

## APIs, Types, And Functions
Features select test engines, allocator backends, portable/SSE builds, memory profiling, and failpoints. Dependencies include API versioning, causal timestamps, concurrency manager, raftstore, resolved-ts, grpcio, protobuf, online config, PD client, engine traits, and TiKV core crates. Test targets include integration and failpoint suites; benchmark target `cdc_event` measures event sizing.

## Control Flow
Cargo feature selection controls engine backend and test/failpoint compilation. Failpoint tests are isolated in a separate target to avoid interfering with normal tests.

## State And Persistence
The manifest has no runtime state. It controls compile-time composition of CDC service code.

## Dependencies And Integration Points
Shows CDC's integration breadth: storage engines, raftstore events, resolved timestamp tracking, causal timestamp provider, gRPC streaming, and online config.

## Risks And Test Signals
Feature matrix complexity is a risk, especially allocator and engine-test feature interactions. Separate integration/failpoint tests and the event-size benchmark indicate both correctness and stream sizing are important.
