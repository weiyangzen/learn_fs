# sources/storage-engines/pebble/internal/testutils/errors.go

## Purpose
This file provides generic helpers that simplify tests where returned errors are expected to be nil.

## Important APIs, Types, and Functions
`CheckErr[V](v, err)` returns `v` or panics on `err`. `CheckErr2[V,W](v,w,err)` returns two values or panics on `err`.

## Control Flow and State
Both helpers are stateless and branch only on whether `err` is nil. They panic rather than fail a `testing.T`, so they are most useful in setup expressions or where the caller wants panic-based simplification.

## Dependencies and Integration
There are no imports. The helpers are generic and can wrap arbitrary functions returning one or two values plus error.

## Risks and Edge Cases
Panics do not automatically mark helper stack frames or produce `require`-style test messages. They should not be used when a test needs precise failure attribution or error matching.

## Test Signals
No direct tests are included. The code is simple, and coverage is indirect through tests that use these helpers.
