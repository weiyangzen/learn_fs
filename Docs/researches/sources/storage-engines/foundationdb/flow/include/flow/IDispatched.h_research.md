# sources/storage-engines/foundationdb/flow/include/flow/IDispatched.h

## Purpose
`IDispatched.h` provides static registration/dispatch helpers for mapping keys to functions or factories at program initialization.

## Important APIs, Types, And Functions
The template `IDispatched<T,K,F>` exposes static `dispatches()` and `dispatch()`. Macros include `REGISTER_DISPATCHED`, `REGISTER_DISPATCHED_ALIAS`, `REGISTER_COMMAND`, and `REGISTER_FACTORY`.

## Control Flow
Static registration structs insert entries into a process-local `std::map` during static initialization. `dispatch(k)` looks up the key and throws `internal_error()` when missing. Alias registration copies an already-registered target function.

## State And Persistence Behavior
State is a function-local static map per dispatch type. It persists for the process lifetime and is not serialized.

## Dependencies And Integration Points
It depends on `flow/flow.h`, `std::map`, Flow `ASSERT`, and `internal_error()`. It is used by command-style dispatchers and factories where pluggable implementations register themselves.

## Risks And Edge Cases
Static initialization order matters, especially for aliases requiring the target to exist first. Duplicate keys assert. Missing keys throw internal errors rather than returning optional results.

## Test Signals
Registration tests should cover duplicate rejection, missing-key errors, alias registration order, factory construction, and separate maps per dispatch type.
