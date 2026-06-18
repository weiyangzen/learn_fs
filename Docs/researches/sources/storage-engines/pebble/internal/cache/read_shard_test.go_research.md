# sources/storage-engines/pebble/internal/cache/read_shard_test.go

## Purpose
This file tests read-miss coordination, including deterministic state transitions and randomized concurrent readers for many blocks and handles.

## Important APIs, Types, And Functions
`testReader` wraps async `getWithReadEntry` and `waitForReadPermissionOrHandle`. Helpers include `newTestReader`, `getAsync`, `waitUntilFinishedWait`, `setReadValue`, and `setError`. `TestReadShard` runs `testdata/read_shard` commands. `testSyncReaders` and `TestReadShardConcurrent` run concurrent `Handle.GetWithReadHandle` calls.

## Control Flow
The datadriven test initializes a shard, starts named readers with optional canceled contexts, waits for each to either receive a value, error, or turn to read, injects success/error results, and prints `readMap` length or resident shard entries. The randomized test creates 50 block targets with five readers each; one reader per block may error, while others either publish or consume the expected value.

## State And Persistence Behavior
Only in-memory shard/read-entry state is used. The test verifies `readMap` cleanup and cache insertion state after transitions.

## Dependencies And Integration Points
It depends on `datadriven`, `testing/synctest`, `context`, `crypto/rand`, `testify/require`, the public `Handle.GetWithReadHandle` API, and internal `readEntry` APIs.

## Risks And Edge Cases
The tests intentionally cover canceled contexts, handoff after read errors, concurrent waiters, and ensuring values are available even if not yet in the resident block cache. Randomized coverage can miss some interleavings, but deterministic datadriven cases pin the state machine.

## Test Signals
Signals include map length returning to zero, expected printed shard entries, no unexpected errors in concurrent readers, and equality of every returned value to the per-block payload.
