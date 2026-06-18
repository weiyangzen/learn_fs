# sources/storage-engines/foundationdb/flow/JsonTraceLogFormatter.h

## Purpose
Declares the JSON trace-log formatter used by Flow tracing.

## Important APIs, Types, And Functions
`JsonTraceLogFormatter` final implements `ITraceLogFormatter` and `ReferenceCounted<JsonTraceLogFormatter>`, declaring extension/header/footer/event-formatting and refcount methods.

## Control Flow
No runtime logic in the header; it defines the interface contract implemented in `JsonTraceLogFormatter.cpp`.

## State And Persistence Behavior
No fields are declared, so formatter instances are stateless aside from reference count.

## Dependencies And Integration Points
Includes `FastRef` and `Trace`. Used wherever trace setup selects JSON output.

## Risks And Edge Cases
Any change to method signatures affects trace formatter polymorphism. The header lacks include guards beyond the implicit compiler handling of repeated includes, so repeated inclusion depends on surrounding build conventions if not otherwise guarded.

## Test Signals
Build/link conformance and trace formatter runtime use are the expected signals.
