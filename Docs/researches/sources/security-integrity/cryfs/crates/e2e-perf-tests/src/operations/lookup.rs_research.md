# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/lookup.rs

## Purpose
This module defines the `lookup` performance counter suite for resolving child names under parent nodes. It tests existing and missing children from root, nested, and deeply nested directories.

## Important APIs, Types, And Functions
The module uses `perf_test_only_fuser!` because fuse-mt does not expose a lookup operation. Registered cases are `existing_from_rootdir`, `notexisting_from_rootdir`, `existing_from_nesteddir`, `notexisting_from_nesteddir`, `existing_from_deeplynesteddir`, and `notexisting_from_deeplynesteddir`. The operation is `filesystem.lookup(parent, PathComponent)` with `unwrap()` for existing cases and `unwrap_err()` for missing cases.

The code imports `FixtureType` but uses `unreachable!` for `Fusemt` branches in expectations as an additional guard.

## Control Flow
Existing cases create the target file in setup, returning the parent node when needed, then look up the child by name. Missing cases create only the parent directory, then look up a missing name and require an error. Expected counts branch between fuser with and without inode cache.

## State And Persistence Behavior
Lookup is read-only. Existing lookups load the parent directory and the child metadata, so they have more loads than missing lookups, which stop after reading the parent directory. Deep parent nodes add traversal reads for no-cache fuser. No blob writes, resizes, flushes, or stores are expected.

## Dependencies And Integration Points
This suite exercises fuser-specific lookup behavior and validates the perf macro's ability to disable fuse-mt. It integrates with directory creation and file creation setup but measures only lookup. It is a direct signal for inode cache and path resolution behavior.

## Risks And Edge Cases
The missing-name tests assert only that an error exists, not the exact error code. The suite does not cover directories or symlinks as lookup targets, invalid names, root lookup by special names, case sensitivity, or permission-denied lookup. Expected counts have TODO uncertainty.

## Test Signals
Signals include existing-vs-missing load deltas, root-vs-nested-vs-deep traversal costs, and fuser inode-cache effects. Any accidental mutation or fuse-mt registration would be caught by counters or unreachable branches.
