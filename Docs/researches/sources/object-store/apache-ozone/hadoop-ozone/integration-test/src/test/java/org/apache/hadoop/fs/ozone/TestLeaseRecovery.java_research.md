# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestLeaseRecovery.java

Purpose: integration tests for `RootedOzoneFileSystem.recoverLease` and `isFileClosed` on hsynced open files, including datanode block-length probing, container closure, forced recovery, OM connection failure, wrong path handling, and partial block edge cases.

Important APIs/types/functions: `closeIgnoringKeyNotFound` and `closeIgnoringOMException` normalize expected close failures after recovery. `testRecovery` parameterizes file sizes around block boundaries. Other tests cover no final hsync/hflush on the last block, OBS bucket rejection, finalizeBlock failure logging, closed pipeline recovery, `GetCommittedBlockLength` timeout/exception handling, OM outage, missing file, empty block list, partial hsync block, and equal block counts in open-file and file tables. `closeLatestContainer`, `verifyData`, and `getData` support the scenarios.

Control flow: setup creates a three-DN FSO cluster with hsync enabled, zero lease soft limit, disabled flush delay, and a rooted OFS default URI. Each test creates a unique file, writes and hsyncs data, writes additional data with or without flush, triggers a recovery path, asserts closure state and file length, then closes the stale stream expecting key-not-found or lease-recovery exceptions.

State and persistence behavior: recovery commits or truncates open-key state into the final file depending on datanode block-length evidence. If all committed-length probes time out and force recovery is enabled, OM's known hsynced length becomes final. Closing containers or pipelines simulates stale block state. After successful recovery the original stream's open key is gone.

Dependencies and integration points: uses `RootedOzoneFileSystem`, `MiniOzoneCluster`, SCM container/pipeline managers, `OzoneTestUtils.closeContainer`, `KeyValueHandler` fault injection, `FaultInjectorImpl`, `XceiverClientGrpc` logs, and OM exceptions. It is marked flaky for HDDS-11323.

Risks: asynchronous pipeline closure, RPC timeout tuning, and forced recovery via system property can make tests timing-sensitive. Error assertions depend on log messages and exception wrapping. Shared fault injectors must be reset between tests.

Test signals: validates that recovery is idempotent, rejects unsupported bucket layouts and wrong files, preserves readable data across partial/unflushed writes when evidence is available, fails or truncates predictably when evidence is unavailable, and survives OM restart recovery.
