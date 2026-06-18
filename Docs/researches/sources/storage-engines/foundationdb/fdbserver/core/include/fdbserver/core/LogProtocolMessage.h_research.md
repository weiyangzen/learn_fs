# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/LogProtocolMessage.h

## Purpose
This file defines a reserved transaction-log message that announces the protocol version used to deserialize subsequent mutation messages on a storage-server tag stream.

## Important APIs, Types, And Functions
`LogProtocolMessage` serializes a leading `MutationRef::Reserved_For_LogProtocolMessage` byte followed by `IncludeVersion()`. Helpers include `toString`, `startsLogProtocolMessage`, `isNextIn`, and the `applyVersionStartingHere` read/write overloads.

## Control Flow
Commit/log code injects this message into the same stream as mutations. Consumers peek one byte to distinguish it from normal `MutationRef` data, then apply the embedded protocol version before decoding later messages.

## State And Persistence Behavior
The message is persisted in the TLog stream like other log messages and affects in-memory decoding state for the reader. It carries no payload beyond version metadata.

## Dependencies And Integration Points
It depends on `FDBTypes`, `CommitTransaction`, mutation type reservations, and Flow serialization. It integrates with TLog peeking, storage-server recovery, and any future mutation serialization migration.

## Risks And Edge Cases
The leading byte must remain permanently reserved or storage servers could misclassify mutations. The comment notes this mechanism has not been exercised by an actual mutation format change, so compatibility testing is critical before relying on it.

## Test Signals
Tests should verify byte discrimination, serialization round trips across protocol versions, mixed streams of protocol messages and mutations, and recovery from logs containing the marker.
