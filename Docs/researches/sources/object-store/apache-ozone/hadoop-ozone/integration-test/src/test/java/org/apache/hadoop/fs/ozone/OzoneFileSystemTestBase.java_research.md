# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/OzoneFileSystemTestBase.java

Purpose: abstract shared test suite for Ozone Hadoop `FileSystem` behavior across O3FS and OFS variants. It contains reusable assertions for listing, implicit directories, recursive delete, invalid path handling, capabilities, timestamp mutation, and rename edge cases. Concrete subclasses provide `getFs`, `pathUnderFsRoot`, key lookup, child-key naming, and layout-specific verification hooks.

Important APIs/types/functions: `listStatusIteratorOnPageSize` configures a small listing page size and verifies iterator paging; `listLocatedStatusForZeroByteFile` checks zero-length files expose no block locations; `createKeyWithECReplicationConfig` validates EC replication configuration through `OzoneKeyDetails`; `verifyListStatus`, `listStatusOnRoot`, and `listStatusOnSubDirs` encode immediate-child listing semantics. Rename helpers cover file-to-file, file-to-directory, parent rename, self-subdir prevention, and missing destination parent failures.

Control flow: each helper creates a focused tree under the supplied root, performs filesystem operations through the abstract `FileSystem`, asserts Hadoop-compatible status or exception behavior, then cleans up the tree. Some helpers additionally query OM key metadata to distinguish real key rows from synthetic filesystem parents.

State and persistence behavior: the tests intentionally exercise Ozone's object-store-backed directory model. Creating a deep child must not automatically persist parent directory keys, but listing and status calls must synthesize parent directories. Deleting the last child may create a fake parent dir key, and recursive deletes must remove batched children. EC tests persist replication metadata and confirm it is stored on the created key.

Dependencies and integration points: depends on Hadoop `FileSystem`, `Path`, `FileStatus`, `RemoteIterator`, `ContractTestUtils`, Ozone `OzoneConfiguration`, `OzoneKeyDetails`, and OM exceptions. It integrates with concrete O3FS/OFS test subclasses and their key-table lookup implementations.

Risks: assertions depend on subtle synthetic-directory semantics and ordering-insensitive listing behavior. Iterator paging uses a disabled FS cache so stale cached configuration would hide page-size bugs. Tests that inspect OM key rows are sensitive to bucket layout and key-name composition differences.

Test signals: failures indicate regressions in listStatus/listStatusIterator parity, directory materialization, delete batching, rename validation, EC replication config propagation, path validation, path capabilities, or mtime handling.
