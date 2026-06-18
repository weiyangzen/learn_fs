# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/create_file.rs

## Purpose
This module defines the `create_file` performance counter suite. It measures creating files from the root directory, a nested directory, and a deeply nested directory, for both absent and already-existing names.

## Important APIs, Types, And Functions
The registered cases are `notexisting_from_rootdir`, `existing_from_rootdir`, `notexisting_from_nesteddir`, `existing_from_nesteddir`, `notexisting_from_deeplynesteddir`, and `existing_from_deeplynesteddir`. They use `filesystem.create_file(parent, PathComponent)` as the operation under test. Setup helpers include `mkdir`, `mkdir_recursive`, and an initial `create_file` for existing-name cases.

The file imports `ActionCounts`, `FixtureType`, `TestDriver`, `TestReady`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `AbsolutePath`, and `PathComponent`.

## Control Flow
Absent-name cases set up only the parent directory, then call `create_file` and unwrap success. Existing-name cases create the file during setup, then call `create_file` again during measurement and intentionally ignore the returned `Result`; this measures the failed/rollback path without requiring success.

## State And Persistence Behavior
Successful creation allocates a new store object and updates the parent directory. Expected counters include `store_create`, parent `store_load`, `blob_resize`, parent and child `blob_write`, `blob_flush`, high-level `store_flush_block`, low-level `exists`, and low-level `store`. Existing-name attempts still show `store_create` followed by `store_remove_by_id` / `store_remove`, implying speculative creation is rolled back when the name collision is detected.

Path depth affects load/read counts. Root creation has constant counts; nested and deep cases branch on `FixtureType`, with no-cache fuser carrying extra parent-path traversal work.

## Dependencies And Integration Points
`perf_test!` expands the cases for all fixture types and atime modes. The test driver supplies an instrumented in-memory blockstore in normal test mode. These tests integrate with path parsing through `PathComponent::try_from_str` and `AbsolutePath::try_from_str`.

## Risks And Edge Cases
The existing-name tests discard the error and therefore only assert performance side effects, not the exact error type. The module does not cover invalid names, root-as-file conflicts, permission failures, or concurrent creation. TODOs indicate uncertainty about expected counts, particularly what root or parent blocks are loaded and why no-cache fuser differs.

## Test Signals
Important signals are successful creation counters (`store_create`, `blob_write`, `blob_flush`, `exists`, `store`) and rollback counters (`store_remove_by_id`, `store_remove`, `remove`). Counter differences across root, nested, and deep paths indicate lookup and parent-directory update cost.
