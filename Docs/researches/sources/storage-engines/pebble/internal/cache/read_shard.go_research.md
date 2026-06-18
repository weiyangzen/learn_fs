# sources/storage-engines/pebble/internal/cache/read_shard.go

## Purpose
This file coordinates concurrent cache misses for the same block. It ensures that only one goroutine at a time reads a missing block, while waiters either consume the successfully read value or receive a turn after an error.

## Important APIs, Types, And Functions
`readShard` owns a Swiss map from cache `key` to `*readEntry` and a pointer to the parent shard. `acquireReadEntry` creates or refs an entry. `readEntry` stores the pending value, `isReading`, lazy waiter channel, accumulated `errorDuration`, read start time, and refcount. `waitForReadPermissionOrHandle`, `unrefAndTryRemoveFromMap`, `setReadValue`, and `setReadError` implement the state machine. `ReadHandle` exposes `Valid`, `SetReadValue`, and `SetReadError`.

## Control Flow
On miss, callers acquire a `readEntry`. The first caller sets `isReading` and returns a valid read handle. Concurrent callers wait on a lazily allocated channel or context cancellation. Success stores a retained value, closes the channel to wake all waiters, inserts into the cache with `markAccessed` if there were concurrent waiters, and unreferences the entry. Failure clears `isReading`, sends one token to let a waiter retry, records duration, and unreferences.

## State And Persistence Behavior
State is volatile and separate from resident cache entries. `readEntry` may retain a value until all waiters release. Entries are removed from `readMap` when their refcount reaches zero and then returned to a pool.

## Dependencies And Integration Points
It integrates with `shard.getWithReadEntry`, `Handle.GetWithReadHandle`, `Value` refs, the parent shard's `set`, context cancellation, and `swiss.Map`.

## Risks And Edge Cases
Risks include leaked read entries when callers fail to call `SetReadValue`/`SetReadError`, context cancellation causing wasted waiting, channel state races, and reference-count imbalance. The contract explicitly permits waiting on a shared load semaphore before doing the read.

## Test Signals
`read_shard_test.go` uses datadriven and randomized concurrent tests to validate turn taking, map cleanup, success fanout, error handoff, cancellation, and cache insertion after successful reads.
