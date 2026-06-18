# sources/storage-engines/pebble/internal/manifest/btree_test.go

## Purpose
This file provides correctness tests, randomized tests, concurrency/clone tests, iterator tests, and benchmarks for the manifest B-tree.

## Important APIs, Types, And Functions
Test helpers include `newItem`, `cmp`, `key`, `Verify`, `verifyLeafSameDepth`, `verifyCountAllowed`, `isSorted`, `checkIter`, `perm`, and `rang`. Correctness tests include `TestBTree`, `TestIterClone`, `TestIterCmpEdgeCases`, `TestIterCmpRand`, `TestBTreeSeek`, `TestBTreeInsertDuplicateError`, `TestBTreeCloneConcurrentOperations`, `TestIterStack`, `TestIterEndSentinel`, and `TestRandomizedBTree`. Benchmarks cover insert, delete, delete/insert, clone-heavy mutation, iterator creation, seek, next, and prev.

## Control Flow
The main B-tree test inserts and deletes 768 items in sorted and reverse order, periodically verifying structural invariants and iterator order. Clone tests recursively create copy-on-write clones in goroutines, mutate subsets independently, and verify all snapshots. Randomized testing compares the tree against a map of file numbers across thousands of insert/delete/iterate operations. Benchmarks build varied tree sizes and isolate specific operations.

## State, Persistence, And Side Effects
All state is in-memory. Tests initialize physical backing metadata so deleting from the B-tree can produce obsolete table backings where expected. Concurrent clone tests intentionally exercise atomic node refs and independent mutation after cloning, then release all trees and expect each original backing to become obsolete exactly once.

## Dependencies And Integration Points
The file depends on `cmp`, `fmt`, `math/rand/v2`, reflection, slices, sync, testing, time, CockroachDB errors, Pebble `base`, build tags, and `testify/require`. It integrates B-tree internals with `LevelIterator`, `TableMetadata`, obsolete-file accounting, and build-tag-driven race/slow-test behavior.

## Risks And Edge Cases
Tests rely on unexported internals because they are in package `manifest`. Randomized tests use time seeds and log them for reproduction. Expensive full-tree verification is throttled in `TestBTree` to control runtime while still covering split/merge boundaries. Concurrency tests validate clone isolation, not arbitrary concurrent mutation of the same tree.

## Test Signals
Passing tests strongly indicate B-tree shape invariants, sorted order, subtree counts, iterator sentinels, seek logic, duplicate detection, copy-on-write behavior, and ref/unref accounting are intact. Benchmarks provide performance baselines across tree sizes and clone patterns.
