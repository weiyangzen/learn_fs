# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBCheckpointServlet.java

Purpose: `DBCheckpointServlet` serves current OM/SCM metadata database checkpoints as tar streams and supports optional SST exclusion for incremental snapshot transfer.

Important APIs/types/functions: `initialize()` binds a `DBStore`, metrics, authorization flags, admin users/groups, SPNEGO flag, no-op bootstrap lock, and temp bootstrap directory. `doGet()` handles query-parameter requests; `doPost()` requires multipart form data. `generateSnapshotCheckpoint()` performs authorization and flush parsing. `processMetadataSnapshotRequest()` creates temp dir, obtains checkpoint, writes tar data, updates metrics, and cleans up. Static helpers parse form data and extract SST exclusion lists. `writeDbDataToStream()` delegates to `HddsServerUtil.writeDBCheckpointToStream()` and is overrideable. `NoOpLock` implements a bootstrap lock that does nothing.

Control flow: requests are rejected if DB store is null, authorization fails, or POST is not multipart. Authorized requests parse `flush` and SST exclusions, acquire a write lock, create a temp bootstrap subdirectory, call `dbStore.getCheckpoint(flush)`, set tar response headers, stream checkpoint data excluding requested SSTs, update timing/count metrics, then delete temp directories and clean checkpoint resources. Exceptions set HTTP 500 and increment failure count.

State and persistence: servlet fields hold DB store, metrics, authorization/admin state, lock, and bootstrap temp directory. It creates/cleans temporary directories under the DB parent. Checkpoints are filesystem artifacts managed by `DBCheckpoint.cleanupCheckpoint()`.

Dependencies/integration: used by OM/SCM DB checkpoint servlet subclasses. Depends on servlet APIs, Commons FileUpload/IO, Ozone admins, DBStore/DBCheckpoint, BootstrapStateHandler, Ratis `UncheckedAutoCloseable`, and RocksDB SST naming constants.

Risks: local variable `excludedSstList` is never populated from `receivedSstFiles`, so logging, incremental metric, and excluded-count metric appear inconsistent with actual exclusions passed to streaming. Authorization only checks admin membership when both authorization and SPNEGO are enabled; otherwise authorization-enabled requests still require a principal but `hasPermission()` returns true if SPNEGO is disabled. Temp directory cleanup failure is logged but not surfaced after response streaming.

Test signals: `TestOMDbCheckpointServlet`, `TestSCMDbCheckpointServlet`, inode-based transfer tests, and Ratis snapshot transfer tests cover authorization, metrics, checkpoint streaming, locks, SST exclusion handling, and cleanup behavior.
