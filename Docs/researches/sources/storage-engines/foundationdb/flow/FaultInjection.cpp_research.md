# sources/storage-engines/foundationdb/flow/FaultInjection.cpp

## Purpose
Defines the global switches and callbacks used by Flow fault-injection call sites.

## Important APIs, Types, And Functions
`should_inject_fault` and `should_inject_blob_fault` are global function pointers taking context, file, line, and error code. `faultInjectionActivated` gates injection globally. `enableFaultInjection(bool)` toggles the activation flag.

## Control Flow
This file only assigns state. Actual fault-injection decisions happen at call sites that check the activation flag and invoke the callbacks.

## State And Persistence Behavior
All state is in-process global state. It is not synchronized here and is not persisted.

## Dependencies And Integration Points
Integrates with `flow/FaultInjection.h`, simulation, blob-specific testing, and code paths that construct injected `Error` values.

## Risks And Edge Cases
The function pointers default to null, so callers must guard them. Global mutable state can leak between tests if not reset. Thread-safety depends on higher-level usage because this file provides no locking or atomics.

## Test Signals
No local test. Signal comes from simulation/fault-injection tests that enable or disable injection and validate `Error::asInjectedFault()` propagation.
