# sources/storage-engines/pebble/internal/cache/clockpro_tracing.go

## Purpose
This build-tagged file provides cache-level trace recording when Pebble is built with `tracing`.

## Important APIs, Types, And Functions
`func (c *Cache) trace(msg string, refs int64)` formats a message with the reference count and `debug.Stack`, then appends it to `c.tr.msgs` under `c.tr`'s mutex.

## Control Flow
Trace call sites invoke this method to capture stack-local history. The method serializes updates so multiple goroutines may record traces safely.

## State And Persistence Behavior
The only state is the in-memory trace slice on `Cache`. There is no persistence, and trace accumulation may increase memory use in diagnostic builds.

## Dependencies And Integration Points
It depends on `fmt` and `runtime/debug` and pairs with `clockpro_normal.go`. It complements `refcnt_tracing.go`, which traces per-value reference operations.

## Risks And Edge Cases
The implementation can be expensive because every trace captures a stack and appends a string. It is correctly restricted to tracing builds, but unbounded trace growth can matter during long diagnostic runs.

## Test Signals
No direct tests exist in this subset. Compile-time build tags and manual tracing/debug runs are the expected validation mechanism.
