# sources/storage-engines/foundationdb/flow/EventTypes.h

## Purpose
Declares the serializable descriptor used to expose trace event name/id pairs through Flow's typed descriptor system.

## Important APIs, Types, And Functions
`TraceEventNameIDDescriptor` contains `Standalone<StringRef> name` and `Standalone<StringRef> id`. The `Descriptor<TraceEventNameIDDescriptor>` specialization maps it to type name `TraceEventNameID` with fields `name` and `id`.

## Control Flow
There is no runtime control flow beyond template instantiation by descriptor-aware serialization or metric code.

## State And Persistence Behavior
Instances own standalone string data through arenas. The header itself has no global state and performs no I/O.

## Dependencies And Integration Points
Depends on `flow/flow.h` and `flow/TDMetric.h`. It integrates with TraceEvent metadata/metric plumbing that needs a reflected schema for event names and ids.

## Risks And Edge Cases
Schema changes here can affect consumers expecting the exact `TraceEventNameID` descriptor shape. Since both fields are standalone strings, callers must still manage content size and validity elsewhere.

## Test Signals
No direct test in this file. Build-time descriptor instantiation and downstream trace/TDMetric serialization tests are the practical signal.
