# sources/storage-engines/foundationdb/flow/include/flow/ActorContext.h

Purpose: declares actor context tracking and dump APIs when `WITH_ACAC` is enabled, with no-op-compatible types otherwise.

Important APIs/types/functions: `ActorIdentifier`, `ActorID`, `ActiveActor`, `ActorExecutionContext`, `ActiveActorHelper`, `ActorExecutionContextHelper`, `ActorContextDumpType`, `encodeActorContext`, `dumpActorCallBacktrace`, `DecodedActorContext`, and `decodeActorContext`.

Control flow: enabled builds can register/unregister active actors through RAII helpers, track block execution context, dump actors, encode current context, and decode serialized context. Disabled builds typedef identifiers and provide minimal structs/helpers.

State/persistence: enabled mode implies global actor context state managed outside this header; serialized context strings can be persisted in traces/logs.

Dependencies/integration: Flow random/UID, FastAlloc/FastRef, mutex/vector/ostream in enabled mode. It integrates with actor compiler instrumentation and debugging.

Risks: disabled mode changes functionality substantially while preserving compile compatibility. Actor IDs and context dumps must be thread-safe in implementation.

Test signals: build variants with and without `WITH_ACAC`; runtime actor context dumps and decode round trips.
