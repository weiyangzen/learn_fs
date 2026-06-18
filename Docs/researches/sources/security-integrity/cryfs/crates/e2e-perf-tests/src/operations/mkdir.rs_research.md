# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/mkdir.rs

## Purpose
This file defines end-to-end performance counter tests and benchmark cases for CryFS `mkdir` behavior. It exercises successful and failing directory creation from the root directory, from a one-level nested directory, and from a deeply nested directory. The main signal is not functional output alone, but the expected action counts across the tracked blobstore, high-level blockstore, and low-level blockstore layers.

## Important APIs, types, and functions
- Uses `crate::perf_test_macro::perf_test!` to register six test cases: `notexisting_from_rootdir`, `existing_from_rootdir`, `notexisting_from_nesteddir`, `existing_from_nesteddir`, `notexisting_from_deeplynesteddir`, and `existing_from_deeplynesteddir`.
- Each case accepts `impl TestDriver` and returns `impl TestReady`, building a test via `create_filesystem().setup(...).test(...).expect_op_counts(...)`.
- Calls `FilesystemDriver::mkdir`, `FilesystemDriver::mkdir_recursive`, and path constructors `PathComponent::try_from_str` and `AbsolutePath::try_from_str`.
- Expected counts are expressed with `ActionCounts`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, and fixture-specific branches on `FixtureType`.

## Control flow
Every test creates a fresh CryFS filesystem, performs setup, resets setup counters and cache through the shared harness, executes exactly one `mkdir` attempt, then asserts the accumulated counters. Root tests call `mkdir(None, ...)`. Nested tests create or recursively create the parent first and pass the returned node handle as `Some(parent)`. Existing-name tests deliberately call `unwrap_err()` after pre-creating the target name, while non-existing-name tests call `unwrap()`.

## State and persistence behavior
Successful creates allocate a new directory blob and update the parent directory blob. Nested creates also update timestamp metadata in ancestor directories, which is why nested successful cases expect more writes and stores than root creates. Existing-name tests still create a candidate directory blob first, then remove it after the parent insertion fails, so they expect `store_create` plus `store_remove_by_id`/`store_remove`. Setup-created state is persisted into the test filesystem but counters are reset before the measured operation.

## Dependencies and integration points
The file integrates with the generic performance harness in `test_driver.rs`, the fixture stack in `filesystem_fixture.rs`, and both FUSE-facing drivers selected by `perf_test!`. It relies on the fixture's tracking stores to observe logical blob operations and physical block operations. It also depends on the filesystem driver's node-handle semantics: fuser without inode cache repeatedly resolves paths, while fuser with inode cache can reuse setup handles more cheaply.

## Risks and observations
Several expected-count branches are annotated as uncertain. Deep and nested fuser-without-cache paths expect substantially more loads/read-all/read calls than fuse-mt, with comments attributing this to path-only `CryNode` structures that must repeat lookup work. Existing nested cases expect a low-level `store` even when the logical operation fails, which is called out as suspicious. These tests tightly encode current implementation costs, so legitimate cache, timestamp, or rollback changes will require careful count updates.

## Test signals
`cargo test` without the `benchmark` feature expands these cases across fixture types and atime policies, asserting exact counts with `pretty_assertions`. `cargo bench --features benchmark mkdir` expands them as criterion benchmarks. The strongest coverage signals are: successful root create costs one new blob and one parent update; duplicate create rolls back a speculative blob; path depth and fixture type scale read/load counts; and setup counters do not pollute measured operation counts.
