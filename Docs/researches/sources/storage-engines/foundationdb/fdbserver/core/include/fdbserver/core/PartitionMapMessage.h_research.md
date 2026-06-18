# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/PartitionMapMessage.h

## Purpose
`PartitionMapMessage.h` defines the reserved transaction-log metadata message that carries backup partition-map information from commit proxies to backup workers.

## Important APIs, Types, And Functions
`PartitionMapMessage` wraps a `PartitionMap`, serializes a leading `MutationRef::Reserved_For_PartitionMapMessage` byte and the map, and exposes `toString`, `startsPartitionMapMessage`, and `isNextIn`.

## Control Flow
Commit proxies inject the message into log streams. Consumers discriminate it by peeking the first byte and then update per-tag key-range partition knowledge for backup processing.

## State And Persistence Behavior
The partition map is persisted in the log stream, but this header has no standalone persistent state. It controls how backup workers interpret subsequent tagged mutations.

## Dependencies And Integration Points
It depends on commit transaction types and `BackupPartitionMap.h`. It integrates with backup workers, commit proxies, and TLog stream readers.

## Risks And Edge Cases
The leading reserved byte must not collide with mutation types or other metadata messages. Large partition maps can increase log message size and backup catch-up cost.

## Test Signals
Useful tests verify marker detection, map serialization, backup worker consumption, compatibility with ordinary mutations in the same stream, and behavior when partition maps change while backup is running.
