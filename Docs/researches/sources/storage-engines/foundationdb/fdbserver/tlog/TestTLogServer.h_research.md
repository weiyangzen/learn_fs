# sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.h

## Purpose
`TestTLogServer.h` declares the state containers and options used by the TLog server test harness. It keeps test configuration, per-log handles, synchronization promises, and expected commit history in one place.

## Important APIs, Types, And Functions
`TestTLogOptions` reads `UnitTestParameters` for disk queue base/extension, KV store filename/extension, data folder, KV memory limit, tag/log/commit counts, initial version, recovery flag, and replica count. `TLogContext` stores one test TLog's `UID`, `TLogInterface`, optional mock router interface, initialize stream, storage pointers, process/tag ID, and promises indicating created/started/completed states. `TLogTestContext` stores group-wide options, log contexts, expected commit history, `LogSystem`, `ServerDBInfo`, locality values, epoch, and helper methods forwarding to static actor implementations.

## Control Flow
The header only declares state and method entry points. The `.cpp` file fills `TLogTestContext`, starts actors, pushes messages, and peeks/pops data. Promises in `TLogContext` coordinate actor readiness and shutdown.

## State And Persistence Behavior
Persistent state is not managed directly here, but `TLogContext` owns raw pointers to the per-test `IKeyValueStore` and `IDiskQueue` created in the `.cpp`. `TLogTestContext::commitHistory` is the in-memory oracle for recovery and peek validation.

## Dependencies And Integration Points
The header includes FDB types, disk queue and KV store interfaces, log system interfaces, resolver/TLog interfaces, storage server interface, and Flow primitives. These declarations bind the test harness to real production TLog and log-system APIs.

## Risks And Test Signals
There is a signature mismatch risk to watch: the member wrapper names and static declarations must stay aligned with the `.cpp` definitions. Because it exposes raw storage pointers, lifetime is controlled externally by actor shutdown and cleanup helpers.
