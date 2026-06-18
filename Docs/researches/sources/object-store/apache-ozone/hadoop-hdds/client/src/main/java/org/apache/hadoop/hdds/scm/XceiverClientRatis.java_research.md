# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientRatis.java

Purpose: Ratis-backed `XceiverClientSpi` implementation for replicated container writes and read-only Ratis operations.

Important APIs/types/functions: Static factories create clients from pipeline, config, trust manager, and optional error injector. Constructor sets RPC type, retry policy, TLS config, watch replication level, majority size, and commit-info map. `connect` builds a Ratis `RaftClient`. `sendCommandAsync` sends container requests via Ratis async API and converts `RaftClientReply` messages into container responses. `watchForCommit` waits for configured replication level with fallback from all-committed to majority-committed. `updateCommitInfosMap` tracks per-server commit indexes.

Control flow: `sendRequestAsync` first allows error injection. Read-only requests use `async().sendReadOnly`; others use `async().send`. Completion updates metrics, validates success, parses protobuf response, updates commit info on successful container result, records log index and replier datanode. `watchForCommit` returns immediately if local replicated minimum already satisfies the index; otherwise it calls Ratis watch and handles `NotReplicatedException` by extracting commit info or issuing majority watch fallback.

State and persistence behavior: Stores pipeline, atomic Raft client, retry/TLS/config, commit-index map, metrics, watch type, majority count, and error injector. State is process-local and cleared by close.

Dependencies and integration points: Integrates with Apache Ratis, HDDS Ratis helper/message wrappers, tracing, security TLS, xceiver metrics, datastream API, and block stream commit watchers.

Risks: Watch type supports only `ALL_COMMITTED` or `MAJORITY_COMMITTED`; misconfigurations throw at construction. Commit-info map update semantics remove failed nodes after all-commit failure, affecting later minimum calculations. Close wraps IOExceptions as unchecked `IllegalStateException`. Error injection can bypass real Ratis behavior.

Test signals: Tests should cover send success/failure parsing, read-only routing, commit-info updates for all and majority, watch fallback on `NotReplicatedException`, group mismatch propagation, data stream API exposure, and close/connect idempotence.
