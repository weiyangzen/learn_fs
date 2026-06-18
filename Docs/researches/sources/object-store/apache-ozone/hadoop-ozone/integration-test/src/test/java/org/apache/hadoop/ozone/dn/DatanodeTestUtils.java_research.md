# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/DatanodeTestUtils.java

Purpose: Test utility class for injecting and restoring datanode data, file, metadata directory, root directory, and volume failures. It supports integration tests that need deterministic local filesystem damage without permanently corrupting test workspaces.

Important APIs, types, and functions: Public static helpers include `injectDataDirFailure`, `restoreDataDirFromFailure`, `injectDataFileFailure`, `restoreDataFileFromFailure`, `injectContainerMetaDirFailure`, `restoreContainerMetaDirFromFailure`, `simulateBadRootDir`, `simulateBadVolume`, `restoreBadRootDir`, `restoreBadVolume`, `waitForHandleFailedVolume`, and `getHddsVolumeClusterDir`. It works with `StorageVolume`, `HddsVolume`, `MutableVolumeSet`, Apache Commons `FileUtils`, and `GenericTestUtils.waitFor`.

Control flow: Directory and file failure injection generally renames the target to a `.origin` backup path, then replaces it with an incompatible filesystem object: a file where a directory should be or a directory where a file should be. Restore methods delete the incompatible replacement and rename `.origin` back. Metadata directory failure manipulates writable permissions. Bad root/volume simulation removes write permission from root directories, and restore returns permissions. `waitForHandleFailedVolume` polls `MutableVolumeSet.getFailedVolumesList().size()` until the expected number appears.

State and persistence behavior: The utility mutates real filesystem state under datanode temp volumes. It preserves original content under the `.origin` suffix so tests can restore during cleanup. Permission changes alter the ability of `HddsVolume.check` and container IO paths to write, causing volume-health code to detect failures.

Dependencies and integration points: Used by volume failure detection/toleration tests and any datanode test that needs chunk, DB, container metadata, or root volume damage. It integrates with Ozone storage volume abstractions while relying on platform filesystem permission semantics.

Risks: If a test aborts before restore, `.origin` files or directories can remain. Permission behavior varies across platforms and user privileges, especially when tests run with elevated permissions. Renaming open RocksDB directories requires careful cache invalidation in callers. The methods are destructive by design and should stay confined to temp test data.

Test signals: The utility itself has no direct tests here, but callers observe IO exceptions, failed volume counts, and successful restore allowing cluster shutdown/cleanup.
