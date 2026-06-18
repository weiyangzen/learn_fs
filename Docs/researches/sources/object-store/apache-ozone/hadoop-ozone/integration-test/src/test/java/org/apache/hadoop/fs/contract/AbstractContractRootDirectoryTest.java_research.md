# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java

Purpose: `AbstractContractRootDirectoryTest` performs potentially destructive root-directory contract checks and is gated by `TEST_ROOT_TESTS_ENABLED`. It validates root mkdir/delete behavior, root preservation, root listing consistency, and recursive root scans.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, `ContractTestUtils.deleteChildren`, `listChildren`, `dumpStats`, `treeWalk`, iterator converters, `GenericTestUtils.waitFor`, and AssertJ. Constant `OBJECTSTORE_RETRY_TIMEOUT` gives object-store listings time to settle.

Control flow: `setup()` skips unless root tests are explicitly enabled. Tests create and delete a top-level directory, attempt recursive and non-recursive deletion of `/`, and assert root remains a directory. The empty-root non-recursive test first deletes all children with retry logic, then deletes `/` non-recursively and verifies root persists. The non-empty root test creates a file under `/`, expects non-recursive root delete to fail, and cleans up. `testRmRootRecursive` allows either recursive deletion of children or preservation, but root itself must remain. Listing tests clear root, assert `listStatus`, `listFiles`, and `listLocatedStatus` agree, and compare recursive `listFiles` with `treeWalk`.

State and persistence behavior: these tests mutate the filesystem root and are intentionally guarded. They verify root identity persistence even when delete returns true, and they account for delayed listing consistency during root cleanup.

Dependencies and integration points: root path behavior is filesystem-global, so subclasses should only enable this against transient test buckets/volumes. It integrates list/status/delete APIs at the root rather than the normal test path.

Risks and test signals: catches catastrophic root deletion, root file creation, inconsistent root listings, stale root children after cleanup, and recursive listing omissions. The highest operational risk is data loss if enabled against a non-transient filesystem.
