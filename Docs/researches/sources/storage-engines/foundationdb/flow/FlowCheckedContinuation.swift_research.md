# sources/storage-engines/foundationdb/flow/FlowCheckedContinuation.swift

## Purpose
Provides Swift/C++ interop wrappers around Swift `CheckedContinuation` so Flow async operations can resume Swift callers with values or Flow errors.

## Important APIs, Types, And Functions
`ExposeVoidConf<T>` and `_exposeVoidValueTypeConformanceToCpp()` force generated C++ header support for `Void`. `FlowCheckedContinuation<T>` stores optional `CheckedContinuation<T, Swift.Error>`, with `init`, `set()`, `resume(returning:)`, and `resumeThrowing(_:)`. `GeneralFlowError` wraps an optional `Flow.Error`.

## Control Flow
Callers create or set a continuation, then resume it once with a value or with `GeneralFlowError`. Assertions enforce that continuations are present before assignment/resume.

## State And Persistence Behavior
State is the optional continuation and optional wrapped Flow error. Nothing is persisted.

## Dependencies And Integration Points
Imports the generated `Flow` Swift module and uses `@_expose(Cxx)` to make selected Swift declarations visible to C++ interop.

## Risks And Edge Cases
Continuation single-resume safety relies on Swift runtime checks and caller discipline; this wrapper does not nil out `cc` after resuming. `resumeThrowing` currently maps all Flow errors to generic `GeneralFlowError`, leaving detailed mapping as a TODO. Use of underscored `@_expose(Cxx)` depends on Swift interop stability.

## Test Signals
No local test. Build success of Swift/C++ generated headers and Swift async interop tests are the primary signals.
