# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/tests.rs

Purpose: This file is the reusable conformance suite for the low-level `BlockStore` API. It exports `instantiate_lowlevel_blockstore_specific_tests!` and a helper macro that instantiate the same async tests for any implementation satisfying the `LLFixture` contract. The suite validates semantics for `try_create`, `load`, `store`, `remove`, `num_blocks`, `all_blocks`, `exists`, and overhead conversion.

Important APIs and flow: The public macro expands into grouped `tokio::test` modules, while `_instantiate_lowlevel_blockstore_specific_tests!` emits each concrete test function. Tests acquire `f.store().await`, mutate it through low-level reader/writer/deleter traits, call `f.yield_fixture(&store).await` after important state changes, assert exact results such as `TryCreateResult::SuccessfullyCreated` and `RemoveResult::SuccessfullyRemoved`, then explicitly `async_drop()` the store.

State and persistence: The tests exercise block persistence through repeated write/read/remove cycles, duplicate ids, empty data blocks, overwritten blocks, and enumeration after deletion. `yield_fixture` is the integration hook that lets fixtures flush, pause, or validate wrapper-specific durable state between operations.

Dependencies and integration: It uses deterministic helpers from `tests::utils`, the low-level traits from `crate::low_level`, result enums from `crate::utils`, `futures::TryStreamExt` for `all_blocks`, `Byte` for overhead checks, and `assert_unordered_vec_eq` for enumeration order independence. It is pulled into implementation test modules through crate-level macros rather than direct test discovery.

Risks and test signals: The suite gives strong coverage for CRUD and listing contracts but leaves TODO gaps for free-space estimation, optimized writer behavior, and size-changing overwrite behavior. It assumes exact fixture behavior around explicit async drop, so implementations that rely on background flushing need fixture adapters to make those transitions observable.
