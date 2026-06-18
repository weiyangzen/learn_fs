# sources/storage-engines/foundationdb/fdbserver/kvstore/TransactionStoreMutationTracking.h

## Purpose
This header exposes the transaction state store mutation debug hook and macro. Its main job is to keep the feature cheap and disabled by default while allowing local builds to turn on targeted mutation tracing.

## Important APIs, Types, And Functions
`DEBUG_TRANSACTION_STATE_STORE_ENABLED` is the compile-time switch and is currently `0`. `DEBUG_TRANSACTION_STATE_STORE(...)` expands to a short-circuit expression that calls `transactionStoreDebugMutation` only when the switch is true. `transactionStoreDebugMutation` is declared with context string, mutation `StringRef`, trace UID, and optional location string.

## Control Flow
There is no runtime control flow in the header beyond macro expansion. With the switch at zero, the macro short-circuits and the function call arguments after the macro boundary are not evaluated as part of the `&&` expression.

## State And Persistence Behavior
The header declares no state and performs no persistence. The actual tracked keys and trace behavior live in the `.cpp` file.

## Dependencies And Integration Points
It includes `fdbclient/FDBTypes.h` for `StringRef`, `UID`, and `TraceEvent` availability through FDB type headers. It is intended to be included at mutation sites in transaction state store code.

## Risks
Because the switch is a macro in a shared header, enabling it changes compilation behavior wherever the header is included and is blocked for clean builds by the `.cpp`. The macro returns a value from an `&&` expression, so call sites should use it as a trace-expression helper rather than rely on it as a function with stable side effects in disabled builds.

## Test Signals
Useful signals include compilation with the default disabled macro, a local enabled build, clean-build rejection when enabled, and representative call sites proving disabled mode does not serialize or allocate mutation details.
