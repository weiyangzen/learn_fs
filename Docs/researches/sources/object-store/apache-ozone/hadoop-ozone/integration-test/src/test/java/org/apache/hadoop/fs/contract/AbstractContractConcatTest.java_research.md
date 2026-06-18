# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractConcatTest.java

Purpose: `AbstractContractConcatTest` validates `FileSystem.concat(Path, Path[])` for filesystems declaring `SUPPORTS_CONCAT`. It checks target existence, input validation, byte ordering, length accounting, and path capability declaration.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem.concat`, `Path`, `CommonPathCapabilities.FS_CONCAT`, `ContractTestUtils.createFile`, `touch`, `dataset`, `assertFileHasLength`, `readDataset`, `validateFileContent`, and JUnit `assertThrows`. `setup()` skips unsupported filesystems, creates a test directory, writes `srcFile`, and creates a zero-byte source.

Control flow: `testConcatEmptyFiles` creates a target then verifies concatenating an empty source array fails. `testConcatMissingTarget` verifies a missing target fails even when sources exist. `testConcatFileOnFile` writes an identical block to the target, concatenates `srcFile`, asserts the length is doubled, and validates target content as two consecutive blocks. `testConcatOnSelf` rejects using the target as a source. `testFileSystemDeclaresCapability` checks `FS_CONCAT` via path capabilities.

State and persistence behavior: the core persistence expectation is an atomic-enough target update: after concat, target remains a file whose content is previous target data followed by source data. The test does not assert source deletion semantics, so its signal is target correctness rather than complete HDFS concat parity.

Dependencies and integration points: this is capability-gated through contract metadata and integrates with the filesystem under test through the standard Hadoop `FileSystem` API. Concrete Ozone contract tests must provide a concat-capable filesystem and block-length assumptions via `TEST_FILE_LEN`.

Risks and test signals: catches filesystems that accept invalid concat calls, corrupt byte ordering, concatenate self, fail to report `FS_CONCAT`, or expose inconsistent length/content after concat. It is intentionally small and does not cover multi-source or directory-source concat.
