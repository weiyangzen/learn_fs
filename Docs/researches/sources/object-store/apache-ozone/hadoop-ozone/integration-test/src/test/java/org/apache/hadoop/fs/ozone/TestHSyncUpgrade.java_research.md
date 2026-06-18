# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestHSyncUpgrade.java

Purpose: verifies that hsync-related features are blocked before OM layout-feature finalization and available only after upgrade finalization starts and completes.

Important APIs/types/functions: `init` creates a five-DN FSO cluster initialized at the `MULTITENANCY_SCHEMA` layout version, with hsync enabled in configuration but not finalized. `upgrade` runs `preFinalizationChecks` and `finalizeOMUpgrade`. Assertions validate `NOT_SUPPORTED_OPERATION_PRIOR_FINALIZATION` for hsync, `listOpenFiles`, and `recoverLease`.

Control flow: setup configures hsync, open-key cleanup, client buffering, and logging; the test opens OFS, creates a file, expects `outputStream.hsync()` to throw the pre-finalization OMException, checks the OM protocol and filesystem lease recovery APIs also fail, deletes the file, then calls `finalizeUpgrade` and polls progress until done.

State and persistence behavior: before finalization, open file creation may exist but hsync metadata and recovery operations must not be accepted. Finalization mutates OM upgrade state from starting to done through `OzoneManagerProtocol`.

Dependencies and integration points: depends on `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, `OMLayoutFeature`, `UpgradeFinalization`, `OzoneManagerProtocol`, `RootedOzoneFileSystem`, and the same hsync cluster/client config used by normal hsync tests.

Risks: tied to upgrade layout versions and finalization status messages. Polling waits up to 120 seconds and can fail if finalization stalls. The test assumes hsync support is gated by feature finalization, independent of client-side config.

Test signals: protects rolling-upgrade compatibility by proving clients receive explicit unsupported-operation errors before finalization and that OM finalization progresses successfully.
