# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/test_driver.rs

## Purpose
This file implements the builder-style test harness used by e2e performance tests. It lets operation files describe setup, counted operation, optional cache/counter reset behavior, expected counts, and benchmark execution without duplicating runtime plumbing.

## Important APIs, Types, and Functions
The central traits are `TestDriver` and `TestReady`. `TestDriverImpl` stores a blockstore factory, filesystem driver marker, atime update behavior, and in counter-test builds the `FixtureType`. Builder structs model each stage: `TestDriverWithFs`, `TestDriverWithFsAndSetupOp`, and `TestDriverWithFsAndSetupOpAndTestOp`.

Important methods include `create_filesystem`, `create_uninitialized_filesystem`, `setup`, `setup_noflush`, chained `setup_noflush`, `test`, `test_no_counter_reset`, `test_noflush`, `test_noflush_no_counter_reset`, and `expect_op_counts`.

## Control Flow
`TestDriverImpl::new` captures fixture configuration. `create_filesystem` and `create_uninitialized_filesystem` wrap async fixture constructors. `setup` composes setup work with `reset_cache_after_setup`, while `setup_noflush` leaves caches warm. `test` resets counters before the counted operation and resets cache after it; variants selectively avoid counter reset or cache flush.

`expect_op_counts` resolves expected counts for the active fixture and atime behavior and returns `TestReadyImpl`. In counter-test mode, `assert_op_counts` creates a Tokio runtime, constructs the fixture, runs setup and test, gathers totals, and uses `pretty_assertions::assert_eq`. In benchmark mode, `run_benchmark` uses Criterion `iter_batched_ref` with async execution.

## State and Persistence Behavior
The harness owns fixture lifecycle for each test iteration. It controls when caches are flushed and when action counters are reset, which defines what operation files actually measure. It also controls blockstore creation through the supplied factory, enabling in-memory deterministic counts or tempdir benchmark persistence.

## Dependencies and Integration Points
The file integrates with `FilesystemFixture`, `FilesystemDriver`, `ActionCounts`, `FixtureType`, `LLBlockStore`, `OptimizedBlockStoreWriter`, `AtimeUpdateBehavior`, `AsyncDrop`, `AsyncDropGuard`, Tokio, Criterion, and pretty assertions. Every operation file consumes this API.

## Risks and Notes
The generic async builder API is powerful but subtle: a wrong choice between `test`, `test_noflush`, and `test_no_counter_reset` changes measured counts. Benchmark mode uses `RefCell<Option<...>>` to adapt an effectively FnOnce async test to Criterion's FnMut interface and will panic if reused unexpectedly. Runtime creation per assertion is simple but may hide runtime-level variability.

## Test Signals
This file supplies the canonical equality assertion for `ActionCounts`. It is also the source of cache reset semantics, making it the first place to inspect when count expectations shift globally across operation files.
