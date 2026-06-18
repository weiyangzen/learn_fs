# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestScmSafeMode.java

## Purpose
Integration tests for SCM safe mode behavior as observed through OM, SCM client APIs, and OFS filesystem writes. It verifies restricted operations during safe mode, force-exit behavior, container threshold tracking, disabled safe mode, and client retry while SCM leaves safe mode.

## Important APIs and Types
The class `TestScmSafeMode` uses `MiniOzoneCluster`, `StorageContainerManager`, `SCMClientProtocolServer`, `StorageContainerLocationProtocolClientSideTranslatorPB`, `SCMSafeModeManager`, `ContainerManager`, `ContainerInfo`, `EventQueue`, `FileSystem`, `SafeMode`, `FSDataOutputStream`, `OMMetrics`, and `SCMException`. Test methods include `testSafeModeOperations`, `testIsScmInSafeModeAndForceExit`, `testSCMSafeMode`, `testSCMSafeModeRestrictedOp`, `testSCMSafeModeDisabled`, and `testCreateRetryWhileSCMSafeMode`.

## Control Flow
Setup tunes heartbeat/stale/dead intervals, builds the cluster without initially starting datanodes, starts them, and waits for readiness. Tests stop and rebuild the cluster with existing metadata to force SCM safe mode before datanodes report. They then check allocation failure messages, force exit, close containers manually, process event queues, shut down datanodes, and exercise OFS file creation while a helper thread restarts datanodes after an allocate-block failure is observed.

## State and Persistence
Persistent state includes SCM container metadata and OM key/bucket metadata created before restart. Safe mode state is runtime SCM state driven by datanode heartbeats, container reports, threshold counters, and configuration flags. Metrics such as `getNumBlockAllocateFails` are used as synchronization signals.

## Dependencies and Integration Points
The test spans OM allocate-block calls, SCM container allocation and pipeline lookup, datanode lifecycle, filesystem `SafeMode` interface, OFS URI configuration, SCM event queues, and container lifecycle transitions.

## Risks and Edge Cases
The class is marked unhealthy for HDDS-3260 and uses sleeps/timeouts around heartbeat-driven state. Some tests rebuild clusters while retaining builder/config state, so ordering and cleanup matter. Assertions depend on exact exception message fragments from safe-mode prechecks.

## Test Signals
Important signals are safe-mode allocation failures, `inSafeMode` and `forceExitSafeMode` API transitions, threshold reaching the configured cutoff after datanodes start, restricted open-container pipeline lookup during degraded safe mode, safe-mode disabled override, and successful file creation after retry while SCM exits safe mode.
