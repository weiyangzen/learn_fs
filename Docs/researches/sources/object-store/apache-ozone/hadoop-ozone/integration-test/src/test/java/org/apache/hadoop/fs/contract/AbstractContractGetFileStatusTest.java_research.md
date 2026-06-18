# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetFileStatusTest.java

Purpose: `AbstractContractGetFileStatusTest` is a broad metadata and listing contract suite. It validates `getFileStatus`, `listStatus`, `listStatusIterator`, `listLocatedStatus`, `listFiles`, filtering, iterator behavior without `hasNext()`, file-vs-directory listing semantics, and missing-path exceptions.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, `PathFilter`, `FilterFileSystem`, `TreeScanResults`, `createSubdirs`, `treeWalk`, iterator conversion helpers, and `touch`. It defines `AllPathsFilter`, `NoPathsFilter`, `MatchesNameFilter`, and `ExtendedFilterFS` to expose protected filtered located-status listing.

Control flow: `setup()` gates on `SUPPORTS_GETFILESTATUS` and initializes `target`. Early tests cover missing file and root status. Empty-directory tests verify `listStatus` and located listings include directories as expected while `listFiles` returns no files. `testComplexDirActions` creates a bounded tree and runs five checks comparing top-level listing, recursive listing, located status, and tree walk results. Missing-path tests assert `FileNotFoundException` across listing variants. File-input tests assert listing a file returns that file. Filtering tests verify accept-all, accept-none, and name filters over directories and files, including next-only iterator consumption.

State and persistence behavior: the class constructs and repeatedly scans directory trees with fixed depth, width, file count, and file size. It verifies metadata consistency by comparing listing `LocatedFileStatus` entries with individual `getFileStatus` calls for directory/file flags, length, and owner.

Dependencies and integration points: integrates heavily with `ContractTestUtils.TreeScanResults` and filesystem iterator contracts. It is especially relevant to Ozone object-store namespace consistency and directory marker behavior.

Risks and test signals: catches stale or incomplete listings, divergent status fields between LIST and HEAD, broken iterator state machines, incorrect behavior when `next()` is called without `hasNext()`, filters ignored on files or directories, missing-path lazy failures, and recursive file listing omissions. It intentionally keeps tree size small to limit object-store test cost.
