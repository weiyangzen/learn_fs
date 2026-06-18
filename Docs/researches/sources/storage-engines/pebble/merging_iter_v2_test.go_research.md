# sources/storage-engines/pebble/merging_iter_v2_test.go

## Purpose
This file provides datadriven tests and shared helpers for `mergingIterV2`. It defines an independent reference merge for point visibility under range deletions and converts compact text fixtures into `iterv2.TestIterData`.

## Important APIs, types, and functions
`mergeLevels` computes expected surviving point keys for a snapshot. `newMergingIterV2FromLevels` wraps test levels in `iterv2.NewTestIter`, sometimes layering invalidating and operation-checking wrappers. `parseMergingTestLevels` and `formatMergingTestLevels` support datadriven input/output. `TestMergingIterV2` runs commands from `testdata/merging_iter_v2`.

## Control flow and state behavior
The `define` command parses levels. Each `L` starts a new level; point keys use internal-key strings and spans use `keyspan.ParseSpan`. The `iter` command constructs a fresh v2 iterator at the requested snapshot and delegates command execution to `itertest.RunInternalIterCmd`.

The reference `mergeLevels` first gathers visible range deletions, then scans visible points and filters points shadowed by any visible range delete with a greater sequence number. It sorts survivors by internal key ordering. This is intentionally simpler than slab logic and serves as a correctness oracle for randomized tests as well.

## Dependencies and integration points
The tests use `datadriven`, `itertest`, `iterv2.TestIter`, `keyspan`, `testkeys.Comparer`, and `base.InternalCompare`. Wrapping with invalidating/op-check iterators increases sensitivity to illegal key retention and invalid iterator operation sequences.

## Risks and test signals
The datadriven path provides readable regression fixtures for boundary and range deletion cases. The helper reference model is valuable but assumes LSM-valid level sequence-number ranges in randomized use. It tests returned point streams, not performance properties such as how often lower levels are parked or how many child seeks occur.
