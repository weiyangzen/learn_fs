# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemDiskQueueAdapter.h

## Purpose
Declares an `IDiskQueue` adapter that lets `KeyValueStoreMemory` treat the log system as a backing queue for transaction-state/configuration data during recovery and commit processing.

## Important APIs, Types, And Functions
`PeekTxsInfo` carries primary locality, secondary locality, and known committed version for TXS peeking. `LogSystemDiskQueueAdapter` implements `IDiskQueue`, exposes `setNextVersion()`, `getCommitMessage()`, `readNext()`, `getNextReadLocation()`, `push()`, `pop()`, `commit()`, close/error methods, and the factory `openDiskQueueAdapter()`. `CommitMessage` packages pushed messages, a pop target, and an acknowledge promise.

## Control Flow
During recovery the constructor can create a `LogSystemConsumer::peekTxs()` cursor from the TXS popped version and locality info. `push()` stores data for the next commit version, `pop()` records the durable pop target, and `commit()` does not push to TLogs directly; instead it makes a `CommitMessage` available and waits for the caller to acknowledge after calling `LogSystem::push()` and `LogSystemConsumer::pop()`.

## State And Persistence Behavior
The adapter tracks recovery read locations and queued recovery bytes, pending pushed data, popped-up-to version, promise waiters, next commit version, discarded data state, and total recovered bytes. Persistent durability is delegated to the log system and TLogs; the adapter is a coordination layer over log messages.

## Dependencies And Integration Points
Depends on `IDiskQueue`, `LogSystem`, and `LogSystemConsumer`. Implementation references show use by commit proxy, GRV proxy, resolver, and cluster recovery for transaction-state replay and configuration commit discard/ack handling.

## Risks And Edge Cases
Several `IDiskQueue` methods intentionally assert or throw because random reads, push-location reporting, and storage-byte accounting are not supported. Commit correctness depends on the caller honoring the two-phase contract: receive commit message, push/pop externally, then acknowledge. Locality changes during TXS recovery can switch peek behavior, so read ordering and popped-data handling are sensitive.

## Test Signals
Signals are integration tests for recovery and transaction subsystem state, plus implementation-level behavior in `LogSystemDiskQueueAdapter.cpp`. Failures tend to appear as stalled `commit()` futures, missing transaction-state replay, or incorrect configuration recovery.
