# sources/sync-backup/kopia/tests/end_to_end_test/index_recover_test.go

## Purpose
Tests recovery of content indexes after all index blobs are deleted.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestIndexRecover` uses `pretty.Compare` and `clitestutil`.

## Control Flow
The test creates snapshots for three sources, captures `content ls`, deletes every index blob listed by `index ls`, clears cache, verifies indexes and content are no longer visible, runs `index recover --commit`, expects one recovered index, and compares recovered content listing to the original.

## State and Persistence Behavior
Deliberately deletes repository index blobs and rebuilds index state by scanning pack blocks. Cache clearing is required to avoid own-write cache masking the deletion.

## Dependencies and Integration Points
Exercises blob deletion, cache clearing, index listing/recovery, content listing, and snapshot creation.

## Risks
Assumes six initial index blobs and one recovered blob. It verifies content listing equality but not restore from every content.

## Test Signals
Validates that lost indexes make content undiscoverable and `index recover --commit` reconstructs equivalent content metadata.
