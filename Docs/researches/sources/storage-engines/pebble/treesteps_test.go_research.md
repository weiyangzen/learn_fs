# Research: sources/storage-engines/pebble/treesteps_test.go

## Purpose
`treesteps_test.go` is an invariants-build datadriven test that records iterator tree-step visualizations for Pebble iterator implementations. It verifies iterator behavior while also generating visualization URLs for debugging traversal decisions.

## Important APIs, Types, And Functions
`TestTreeSteps` walks `testdata/treesteps`, detects V1 versus V2 fixtures by filename suffix, and supports commands `define`, `level-iter`, `merging-iter`, `level-iter-v2`, `merging-iter-v2`, and `iterator`. `treeStepsStartRecording` configures optional max tree depth and normalizes recording names from datadriven positions.

## Control Flow
Each datadriven file defines a DB with `testkeys.Comparer`, in-memory FS, newest format, disabled automatic compactions, and either iterator stack V1 or V2. Individual commands then construct the requested internal iterator, start a treesteps recording, run iterator commands through `itertest` or user-iterator helpers, finish the recording, and append the visualization URL to textual output.

## State And Persistence
All DB state is in-memory and per test file. Iterator state is transient. The treesteps recording is emitted as a URL rather than persisted here. The build tag `invariants` gates the entire file, and the test skips if `treesteps.Enabled` is false.

## Dependencies And Integration Points
The test integrates DB definition helpers, `internal/treesteps`, V1 `levelIter`/`mergingIter`, V2 `iterv2` iterators, manifest level metadata, `itertest`, and public iterator commands. It is a cross-check between data structure topology and iterator-visible behavior.

## Risks And Edge Cases
Because it is build-tagged, normal test runs may not execute it. Visualization URLs can change if recording naming, tree depth, or iterator topology changes. The test must close DBs and iterators carefully to avoid leaked references. V1 and V2 command names must remain aligned with fixture suffixes.

## Test Signals
Signals include iterator outputs plus treesteps URLs for level iterators, merging iterators, and public iterators across both iterator stacks. It is especially useful for seek optimization, level layout, and merging decisions that are hard to understand from key output alone.
