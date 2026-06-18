
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mock.rs

## Purpose
This testutils-gated module defines a `mockall` low-level blockstore mock that implements the full `LLBlockStore` trait surface. It supports unit tests that need expectations over low-level reads, writes, removes, overhead, and async drop.

## Important APIs, Types, and Functions
- `mock! { pub BlockStore { ... } }` generates `MockBlockStore`.
- Mocked traits: `BlockStoreReader`, `BlockStoreDeleter`, `BlockStoreWriter`, `AsyncDrop`, and marker `LLBlockStore`.
- Each async method is expressed as returning a `BoxFuture` because `mockall` cannot directly mock `async_trait` methods without explicit future signatures.
- Custom `Debug` prints `MockBlockStore`.

## Control Flow
The test-only helper `make_working_mock_block_store()` wires every expectation to an underlying `InMemoryBlockStore` held as `Arc<tokio::sync::Mutex<Option<_>>>`. Methods clone the arc, copy ids/data into owned values for async closures, then delegate to the in-memory implementation. `async_drop_impl()` takes the underlying store out of the `Option` and drops it exactly once.

## State and Persistence Behavior
The mock itself has no persistence; its test backing store is in-memory. The `Option` state prevents reuse after async-drop. Expectations for synchronous methods use blocking locks or `block_in_place`.

## Dependencies and Integration Points
The module depends on `mockall`, `futures::future::BoxFuture`, and CryFS `AsyncDropGuard`. It is exported only under `test` or `testutils` feature from `implementations/mod.rs` and `low_level/mod.rs`.

## Risks and Edge Cases
- The helper uses `blocking_lock()` and `block_in_place()` inside mock implementations; this is acceptable in tests but not a production pattern.
- Expectations must be fully configured or mock calls will fail in test code.
- Because `BlockStoreWriter` rather than optimized writer is mocked, tests that require optimized prefix allocation need other stores.

## Test Signals
The module instantiates the full low-level blockstore test suite against the working mock, demonstrating that the mock can behave like a real store when expectations delegate to `InMemoryBlockStore`.
