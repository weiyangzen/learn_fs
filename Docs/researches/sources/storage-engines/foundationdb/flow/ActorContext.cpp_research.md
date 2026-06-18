# sources/storage-engines/foundationdb/flow/ActorContext.cpp

## Purpose
`ActorContext.cpp` implements optional actor context tracking behind `WITH_ACAC`. It records active actors, their execution stack, and spawn relationships, and can serialize actor context dumps for diagnostics.

## Important APIs, Types, and Functions
Important globals are `g_currentExecutionContext` and `g_activeActors`. `ActiveActor` stores identifier, id, spawn time, and spawner id. `ActiveActorHelper` registers/unregisters active actors. `ActorExecutionContextHelper` pushes/pops execution context. Public functions include `dumpActors`, `dumpActorCallBacktrace`, `encodeActorContext`, and `decodeActorContext`.

## Control Flow
Instrumentation helpers only mutate global tracking state on the main actor thread. Actor construction assigns a thread-local incremental actor id and records the current actor as spawner. Execution-context helpers maintain a stack of active blocks. Encoding writes a dump type, current actor id, and either full active-actor state, current stack, or current call backtrace to a `BinaryWriter`, then base64-encodes the binary payload.

## State and Persistence Behavior
State is process-local diagnostic state and is not durable. Encoded dumps are portable strings carrying a snapshot of selected actor metadata. `decodeActorContext` reads that string back into a `DecodedActorContext`.

## Dependencies and Integration Points
The file depends on `ActorContext.h`, `flow.h`, libb64, Flow serialization, and `g_network`. It contains special logic for Sim2 versus Net2 main-thread detection because simulation may not set Net2 thread state in the same way.

## Risks and Edge Cases
The globals are not guarded by the included mutex, so correctness depends on the main-thread check. Missing actor ids during backtrace currently stop traversal with TODOs. Stack underflow in `ActorExecutionContextHelper` destructor aborts the process, which is appropriate for instrumentation corruption but high impact.

## Test Signals
No local unit tests are defined. Observable signals are emitted diagnostic dumps and crashes on context-stack corruption when `WITH_ACAC` instrumentation is enabled.
