<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go

Purpose: Integration suite stressing concurrent directory listing, lookup/stat, file mutations, directory mutations, and move operations to detect gcsfuse deadlocks and race conditions.

Important APIs, types, and functions: Constants set iteration counts for heavy, medium, and light operations. `concurrentListingTest` embeds `suite.Suite` and carries flags, client, context, and base test name. `createDirectoryStructureForTestCase` creates an explicit directory with two files. Test cases include `Test_OpenDirAndLookUp`, `Test_Parallel_ReadDirAndLookUp`, `Test_MultipleConcurrentReadDir`, `Test_Parallel_ReadDirAndFileOperations`, `Test_Parallel_ReadDirAndDirOperations`, `Test_Parallel_ReadDirAndFileEdit`, `Test_MultipleConcurrentOperations`, `Test_ListWithMoveFile`, `Test_ListWithMoveDir`, and `Test_StatWithNewFileWrite`. `TestConcurrentListing` mounts per flag set and runs the suite.

Control flow: Each test creates its own case directory under the mounted test root, starts goroutines for repeated operations, waits through a `sync.WaitGroup`, and fails on timeout as a possible deadlock/race. The top-level runner handles mounted-directory mode specially; otherwise it iterates built flag sets, configures log file, mounts, runs the suite inside `t.Run` to allow parallel subtests to complete, then unmounts.

State and persistence behavior: Creates, renames, edits, moves, stats, opens, and deletes files/directories through the gcsfuse mount. Saves logs on failure and relies on package-level setup/cleanup outside this file for bucket lifecycle.

Dependencies and integration points: Depends on package globals from the concurrent operations setup file, integration `operations` and `setup` utilities, Cloud Storage client, and testify suite/assert/require. It is sensitive to gcsfuse directory cache, list, lookup, and rename/move internals.

Risks and test signals: Calling `require` assertions inside goroutines can be problematic because failures are reported from non-test goroutines; however timeouts and error assertions still expose many failures. Long timeouts reflect slow listing without kernel list cache. Strong signal is absence of deadlock under parallel listings and mutations across multiple flag sets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_listing_test.go -->
