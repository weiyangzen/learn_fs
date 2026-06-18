# sources/storage-engines/foundationdb/flow/include/flow/FaultInjection.h

## Purpose
`FaultInjection.h` declares macros and global hooks for injecting Flow errors at annotated source locations during simulation or testing.

## Important APIs, Types, And Functions
It defines `INJECT_FAULT`, `SHOULD_INJECT_FAULT`, `INJECT_BLOB_FAULT`, `SHOULD_INJECT_BLOB_FAULT`, function pointers `should_inject_fault` and `should_inject_blob_fault`, `faultInjectionActivated`, and `enableFaultInjection()`.

## Control Flow
Injection macros check whether the corresponding hook is installed and whether it chooses the current context/file/line/error code. If so, they throw the requested error factory result tagged with `asInjectedFault()`.

## State And Persistence Behavior
State is global process state: hook pointers and activation flag. Injected status exists on the thrown `Error` object and is not serialized by `Error`.

## Dependencies And Integration Points
It depends on generated `error_code_*` names from `Error.h` at use sites. It integrates with fdbserver actor main, blob fault testing, simulation, and any code path annotated with injection macros.

## Risks And Edge Cases
Macros throw exceptions, so use in destructors or cleanup-sensitive regions is risky. Injected faults should be treated like real faults; checking `isInjectedFault()` too often weakens test value. Hook global state must be reset between tests.

## Test Signals
Enable/disable tests, context matching, blob vs general hooks, injected flag preservation until catch, and simulation tests verifying retry/error paths are useful signals.
