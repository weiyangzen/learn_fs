# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/init.rs

## Purpose
This module defines the `init` performance counter suite for initializing a previously uninitialized filesystem.

## Important APIs, Types, And Functions
The suite registers one case, `init`, with `perf_test!(init, [init,])`. It uses `test_driver.create_uninitialized_filesystem()`, then calls `fixture.filesystem.init().await.unwrap()` in `test_no_counter_reset`. Expected counters include root blob creation and sanity-check reads.

Imports are limited to `FilesystemDriver`, `ActionCounts`, `TestDriver`, `TestReady`, and the three action-count types.

## Control Flow
Setup intentionally does nothing. Unlike most operation tests, the measured phase uses `test_no_counter_reset`, so initialization counters include work performed from the uninitialized fixture state rather than being reset immediately before the operation. The test then asserts a single fixed counter set.

## State And Persistence Behavior
Initialization creates the root directory blob, writes and flushes it, then loads and reads it for filesystem sanity checking. Low-level counts include `exists`, `store`, and `overhead`; high-level counts include `store_try_create`, `store_load`, `store_flush_block`, and `store_overhead`.

## Dependencies And Integration Points
This is the bootstrap performance signal for the filesystem fixture and blockstore stack. It exercises root creation through blobstore, high-level blockstore, and low-level blockstore layers before normal file operations can run.

## Risks And Edge Cases
The test only covers successful initialization of a fresh uninitialized filesystem. It does not cover reinitialization, corrupt root blobs, existing incompatible stores, or initialization failures. A TODO questions why root data is written after creation rather than created with data directly.

## Test Signals
Important signals are exactly one root `store_try_create`, one root low-level `store`, sanity-check load/read counts, and overhead accounting. Changes here indicate bootstrap layout or initialization validation changes.
