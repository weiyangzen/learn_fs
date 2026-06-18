# sources/storage-engines/badger/y/error.go

## Purpose
This file defines lightweight error and assertion helpers used across Badger's internal `y` package.

## Important APIs, Types, And Functions
`Check` fatals on non-nil errors. `Check2` adapts two-return call sites. `AssertTrue` and `AssertTruef` fatal on failed invariants. `Wrap` and `Wrapf` add context, using simple formatting unless `debugMode` is enabled. `CombineErrors` formats one or two errors into a single error.

## Control Flow
Fatal helpers terminate the process via `log.Fatalf`. `Wrap` returns nil for nil input in non-debug mode, but in debug mode it always formats with `%w`; callers rely on `debugMode` remaining false by default. `CombineErrors` avoids nil output only when both inputs are nil.

## State And Persistence Behavior
No persistence. The package-global `debugMode` changes wrapping semantics if toggled.

## Dependencies And Integration Points
These helpers are used throughout Badger for invariant checks, startup failure handling, and context-wrapped errors.

## Risks And Edge Cases
Fatal assertions are unsuitable for recoverable library errors. `Wrap` in non-debug mode does not use Go error wrapping, limiting `errors.Is` on wrapped sentinels. `CombineErrors` loses original error identity by formatting.

## Test Signals
`error_test.go` covers `CombineErrors` output for all nil/non-nil combinations; fatal and wrapping helpers are not directly tested here.
