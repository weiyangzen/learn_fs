# sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_disagg_block_header_version.cpp

## Purpose
Tests disaggregated block-header compatible-version checks to ensure readers compare a page's required compatible version against the current reader version, not the reader's oldest compatible version.

## Important APIs, Types, And Functions
Calls `__ut_block_disagg_header_version_compatible` with constants `WT_BLOCK_DISAGG_COMPATIBLE_VERSION` and `WT_BLOCK_DISAGG_VERSION`.

## Control Flow
The test asserts compatibility for version `1`, the build's compatible version, and the build's current version, then asserts rejection for one greater than current version.

## State And Persistence Behavior
No state. The test models persisted block header compatible-version values.

## Dependencies And Integration Points
Depends on Catch2 and `wt_internal.h`. It guards disaggregated block read compatibility logic.

## Risks And Edge Cases
The bug targeted here only appears when `WT_BLOCK_DISAGG_VERSION` advances beyond `WT_BLOCK_DISAGG_COMPATIBLE_VERSION`; the test is future-proofed for that macro divergence.

## Test Signals
Boolean compatibility results must match current-reader capability boundaries.
