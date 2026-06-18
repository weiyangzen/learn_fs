# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMkdirTest.java

Purpose: `AbstractContractMkdirTest` validates directory creation semantics: create/delete directories, rejecting mkdir over files or under files, trailing slash normalization, recursive ancestor creation, parent preservation, and idempotent mkdir of existing directories.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem.mkdirs`, `Path`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `ContractTestUtils.assertMkdirs`, `createFile`, `dataset`, read/compare helpers, and AssertJ.

Control flow: simple tests create a directory and delete it with both recursive modes. `testNoMkdirOverFile` creates a file, attempts `mkdirs` at the same path, accepts strict or relaxed failure, then verifies file content is intact. `testMkdirOverParentFile` does the same for a child path under a file. `testMkdirSlashHandling` iterates qualified and unqualified paths with no slash, one slash, and multiple trailing slashes, requiring directories to exist at normalized paths. Ancestor tests create deeply nested paths and walk upward to verify every ancestor exists and previously created parents remain. `testCreateDirWithExistingDir` calls `assertMkdirs` twice.

State and persistence behavior: namespace state is central. The tests require `mkdirs` to create missing ancestors, preserve existing directories, never replace file data with directory metadata, and normalize path strings consistently.

Dependencies and integration points: relies on `ContractOptions` only indirectly through relaxed exception handling in the base class. It integrates Ozone's directory marker/key semantics with Hadoop `FileSystem.mkdirs`.

Risks and test signals: catches file/directory conflicts, lost parent directories, non-idempotent mkdir, trailing-slash bugs, and namespace models that allow impossible file-as-parent structures. It does not test permissions or concurrent mkdir races.
