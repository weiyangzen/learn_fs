# sources/storage-engines/pebble/internal/cache/refcnt_normal.go

## Purpose
This file implements the normal, non-tracing reference count used by cache `Value`s.

## Important APIs, Types, And Functions
`refcnt` wraps `atomic.Int32`. `init`, `refs`, `acquire`, and `release` manage counts. `trace` and `traces` are no-ops under `//go:build !tracing`.

## Control Flow
`init` stores an initial count. `acquire` atomically increments and panics if the new count is `<= 1`, catching acquisition after free or uninitialized use. `release` decrements, panics on negative counts, and returns true when the count reaches zero.

## State And Persistence Behavior
The only state is an in-memory atomic integer embedded in a `Value`. There is no persistence.

## Dependencies And Integration Points
It is used by `value.go`, `entry.go`, and cache insertion/acquisition paths. Panic values use `redact.Safe` and `fmt`.

## Risks And Edge Cases
Reference count errors are fatal because they imply use-after-free, double release, or ownership bugs in manual memory. The normal build has no historical trace for debugging; tracing builds provide that.

## Test Signals
Cache tests exercise ordinary acquire/release flows. Invariant and tracing builds improve diagnosis, but this file has no direct unit test.
