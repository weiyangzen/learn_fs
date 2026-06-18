# sources/storage-engines/foundationdb/fdbserver/tlog/TestTLogServer.cpp

## Purpose
`TestTLogServer.cpp` is a local actor-based test harness for creating in-process TLog actors, pushing synthetic commits through a `LogSystem`, peeking and popping committed data, and optionally creating a second TLog generation to validate recovery from old logs.

## Important APIs, Types, And Functions
Helper functions build old-log configuration, storage filenames, and `InitializeTLogRequest`s. `TempStorageFiles` and `StorageResources` manage temporary disk queue and KV store files. `setupPersistentStorage` opens the `IDiskQueue` and memory KV store used by each TLog. `initTLogTestContext` constructs `TLogTestContext` and optionally seeds it from an old generation. Main actors are `getTLogCreateActor`, `TLogTestContext::sendPushMessages`, `TLogTestContext::peekCommitMessages`, `buildTLogSet`, and `startTestsTLogRecoveryActors`.

## Control Flow
The test creates one or more `TLogContext` objects and starts real `::tLog` actors with a `PromiseStream<InitializeTLogRequest>`. After each actor replies with a `TLogInterface`, `buildTLogSet` installs those interfaces into `ServerDBInfo.logSystemConfig` and releases the push actors. `sendPushMessages` builds deterministic set-value mutations, maps tags to log server IDs according to replica/team layout, records expected versions in `commitHistory`, and calls `LogSystem::push`. `peekCommitMessages` peeks each expected version from the selected TLog/tag, decodes the version header and mutation payload, validates key/value data, then sends a pop.

When recovery is enabled, the harness locks old TLogs, builds epoch-two contexts, constructs recovery `InitializeTLogRequest`s with `recoverFrom`, `recoverTags`, `startVersion`, `recoverAt`, and old IDs, then validates the recovered generation through the same peek/pop path.

## State And Persistence Behavior
The test uses real disk queue and KV store implementations with per-TLog filenames derived from TLog ID and epoch. `TempStorageFiles` deletes queue/KV segment files at scope end or after actor shutdown. The expected data model is held in `commitHistory`, keyed by `(tagID, logID)`.

## Dependencies And Integration Points
The file depends on TLog server construction, `LogSystemFactory`, `ServerDBInfo`, Flow transport, mutation serialization, `IDiskQueue`, memory KV store, locality and replication policy types, and unit-test assertions. It exercises the production `tLog` actor rather than a mock.

## Risks And Test Signals
The active `TEST_CASE` definitions are commented out, so the harness may not currently run in normal unit-test discovery. It also assumes specific message serialization order, write tracing branches, and a default replica/team mapping. Still, it is a strong integration signal for TLog commit/peek/pop/recovery because it validates data through the same RPC interfaces used by storage servers and recovery consumers.
