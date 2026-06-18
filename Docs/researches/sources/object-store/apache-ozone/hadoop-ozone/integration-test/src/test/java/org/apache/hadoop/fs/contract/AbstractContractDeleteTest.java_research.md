# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractDeleteTest.java

Purpose: `AbstractContractDeleteTest` validates deletion semantics for files, empty directories, non-empty directories, recursive flags, missing paths, and partial subtree deletion.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem.delete`, `Path`, `ContractTestUtils.writeTextFile`, `rejectRootOperation`, helper assertions `mkdirs`, `assertDeleted`, `assertIsDirectory`, `assertPathDoesNotExist`, and AssertJ/JUnit failure handling.

Control flow: empty directory tests create a path and assert deletion with both recursive modes. Missing-path tests assert delete returns false for both recursive and non-recursive calls after rejecting root-like operations. Non-empty non-recursive deletion writes a child file and expects an `IOException`, then verifies the directory remains. Recursive non-empty deletion checks both directory and child are gone. Deep deletion removes a nested intermediate directory and confirms ancestors remain while the selected subtree disappears. Single-file deletion creates a file under nested directories and deletes that file.

State and persistence behavior: the tests mutate namespace state and verify deletion boundaries. Recursive deletion must remove children, non-recursive deletion must preserve non-empty directories, and deleting a nested directory must not remove higher ancestors.

Dependencies and integration points: integrates with base contract helpers for path creation, root operation rejection, relaxed exception handling, and filesystem cleanup. It assumes concrete filesystems expose enough directory semantics for non-recursive directory deletion to be meaningful.

Risks and test signals: catches delete methods that return true for absent paths, recursively delete too much, allow non-recursive removal of populated directories, leave child entries behind, or accidentally remove ancestors. It does not test delete of open files or concurrent delete/list consistency.
