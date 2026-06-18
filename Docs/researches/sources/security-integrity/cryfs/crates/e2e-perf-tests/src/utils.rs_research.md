# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/utils.rs

## Purpose
This small utility file provides a reusable conditional close helper for performance tests that need both open-handle and release-after-operation variants.

## Important APIs, Types, and Functions
The only API is `pub async fn maybe_close<const CLOSE_AFTER: bool, FS: FilesystemDriver>(...)`. It accepts a mutable `FilesystemFixture`, a filesystem node handle, and a file handle. If the const generic is true, it calls `fixture.filesystem.release(node, file_handle).await.unwrap()`.

## Control Flow
The function branches once on the const generic `CLOSE_AFTER`. The false branch does nothing. The true branch awaits release and panics on error via `unwrap`, matching the style of the performance scenario tests.

## State and Persistence Behavior
When enabled, this helper triggers file-handle release side effects such as flushing dirty file data and metadata through the filesystem driver. When disabled, dirty/open state remains part of the fixture until later fixture teardown and is not included as release-time cost in the counted operation.

## Dependencies and Integration Points
The helper depends on `FilesystemFixture`, `FilesystemDriver`, `LLBlockStore`, `OptimizedBlockStoreWriter`, and `AsyncDrop` trait bounds. It is used by write-like tests to generate `<false>` and `<true>` variants without duplicating release code.

## Risks and Notes
Because release errors are unwrapped, this helper is appropriate for tests that expect release success only. Its generic fixture argument is intentionally broad, which keeps it reusable but makes compile errors verbose if trait bounds drift.

## Test Signals
The helper has no direct tests in this file. Its signal appears in operation tests where `CLOSE_AFTER` changes expected flush, resize, store, and load counts.
