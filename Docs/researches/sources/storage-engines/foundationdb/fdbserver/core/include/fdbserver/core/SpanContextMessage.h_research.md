# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/SpanContextMessage.h

## Purpose
This header defines the legacy span-context metadata message embedded in transaction-log streams to associate subsequent mutations with a `SpanID`.

## Important APIs, Types, And Functions
`SpanContextMessage` stores `SpanID spanContext`, serializes a leading `MutationRef::Reserved_For_SpanContextMessage` byte and the span ID, and provides `toString`, `startsSpanContextMessage`, and `isNextIn`.

## Control Flow
Writers place the marker before mutation messages; readers peek one byte, detect the reserved message, deserialize the span ID, and attach trace context to following mutations.

## State And Persistence Behavior
The message is persisted in TLogs as trace metadata only. It does not affect key-value contents.

## Dependencies And Integration Points
It depends on FDB and commit transaction types, mutation reserved bytes, TLog readers, storage-server replay, and tracing infrastructure.

## Risks And Edge Cases
It overlaps conceptually with `OTELSpanContextMessage`; consumers must handle both encodings. Reserved-byte collisions or incorrect peeking break log stream framing.

## Test Signals
Test signals include marker detection, serialization round trip, mixed metadata/mutation streams, and trace context visibility during storage recovery.
