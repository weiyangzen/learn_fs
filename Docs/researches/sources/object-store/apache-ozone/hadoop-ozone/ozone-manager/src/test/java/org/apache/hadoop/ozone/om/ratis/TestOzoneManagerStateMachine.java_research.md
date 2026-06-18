# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerStateMachine.java

Purpose: extensive unit coverage for `OzoneManagerStateMachine`, including Ratis transaction lifecycle, prepare-mode gating, request execution, error response handling, query handling, last-applied tracking, snapshot creation/loading, leader/configuration notifications, snapshot installation, and lifecycle methods.

Important APIs/types: `OzoneManagerStateMachine`, `OzoneManagerDoubleBuffer`, `RequestHandler`, `OzoneManagerPrepareState`, `TransactionContext`, `RaftClientRequest`, `RaftProtos`, `TermIndex`, `OMRequest`, `OMResponse`, `OMClientResponse`, `OMLockDetails`, `OmRatisSnapshotProvider`, `OMServiceManager`, and `OMMetrics`.

Control flow: setup builds the state machine with mocked OM, double buffer, handler, executor, and service manager. Start-transaction tests validate request parsing, handler validation, and group ID mismatch. Pre-append tests check prepare gate transitions and admin ACL denial. Apply/run-command tests cover leader/follower context paths, double-buffer backpressure, lock detail propagation, IOException conversion to error responses, and runtime termination. Query tests parse read requests. Term-index tests model notified/applied/skipped ranges. Snapshot tests wait for double-buffer flush before flushing DB and setting transaction info. Notification tests cover leader change audit/cache/metrics, peer-list updates, snapshot-provider init on local install, leader-ready cleanup, and Ratis event recording.

State and persistence behavior: mostly mocked, with selected real `OmMetadataManagerImpl` usage for transaction info loading. Critical state includes prepare status, last-notified/applied term indexes, skipped ranges, double-buffer unflushed permits, and metrics event strings.

Dependencies and integration points: central integration boundary among Ratis, OM request handler, double buffer, prepare state, snapshots, audit, HA service manager, and metrics.

Risks: many tests rely on mocks and may not catch serialization or DB batch side effects. Term-index skip behavior is subtle and regression-prone. Runtime error tests intentionally expect `ExitUtils.ExitException`.

Test signals: strong behavioral signals for command validation, prepared-state enforcement, error classification, snapshot safety, leader transitions, peer updates, lifecycle cleanup, and double-buffer synchronization.
