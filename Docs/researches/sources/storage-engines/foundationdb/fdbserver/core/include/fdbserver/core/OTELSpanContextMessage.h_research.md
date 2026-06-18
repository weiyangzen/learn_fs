# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/OTELSpanContextMessage.h

## Purpose
This file defines a reserved log-stream message carrying an OpenTelemetry-style `SpanContext` so TLogs and storage servers can associate subsequent mutations with a transaction trace context.

## Important APIs, Types, And Functions
`OTELSpanContextMessage` stores `SpanContext spanContext`, serializes a leading `MutationRef::Reserved_For_OTELSpanContextMessage` byte plus the context, and provides `toString`, `startsOTELSpanContextMessage`, and `isNextIn`.

## Control Flow
Commit code can push the message before mutation payloads. Consumers peek the first byte, identify the metadata message, deserialize the span context, and apply it to following mutations until superseded.

## State And Persistence Behavior
The message is persisted in transaction logs as stream metadata. It changes tracing attribution but not database contents.

## Dependencies And Integration Points
It depends on `fdbclient/Tracing.h`, FDB types, commit transactions, and mutation reserved type codes. It integrates with TLog serialization, storage-server log replay, and distributed tracing.

## Risks And Edge Cases
Reserved-byte uniqueness is critical. Mixing legacy `SpanContextMessage` and OTEL contexts requires consumers to handle both. Trace metadata should not be allowed to corrupt mutation framing.

## Test Signals
Tests should cover marker-byte detection, serialization round trips, mixed mutation/metadata streams, and trace attribution through TLog peek and storage replay.
