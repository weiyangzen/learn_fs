# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRenameTest.java

Purpose: `AbstractContractRenameTest` validates file and directory rename semantics under multiple contract variants: same-directory rename, missing source, file-over-file behavior, directory into existing directory, missing destination parents, non-empty subdirectory movement, ancestor preservation, and renaming under a file.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem.rename`, `Path`, `FileAlreadyExistsException`, `FileNotFoundException`, `ContractTestUtils.writeDataset`, `writeTextFile`, `verifyFileContents`, `assertListStatusFinds`, `rm`, and contract flags including `RENAME_RETURNS_FALSE_IF_SOURCE_MISSING`, `RENAME_OVERWRITES_DEST`, `RENAME_RETURNS_FALSE_IF_DEST_EXISTS`, `RENAME_CREATES_DEST_DIRS`, and `RENAME_REMOVE_DEST_IF_EMPTY_DIR`.

Control flow: `testRenameNewFileSameDir` writes data, renames, confirms listing and contents. Missing-source behavior branches on whether the contract returns false or throws. File-over-file behavior asserts mutually exclusive flags and verifies destination data based on overwrite/reject outcome. Directory tests cover CLI-style directory-into-existing-directory and POSIX-style replace-empty-destination behavior. Ancestor tests rename trees containing nested directories or files and walk parent chains to ensure source ancestors are gone and destination ancestors exist. Under-file tests create a file as would-be parent and require rename failure with source preserved.

State and persistence behavior: rename must preserve file bytes and move namespace subtrees correctly. Several tests check both source removal and destination creation, not just boolean return values.

Dependencies and integration points: heavily contract-flag driven because Hadoop filesystems differ on rename edge cases. Concrete Ozone contracts must set flags to match their intended rename semantics.

Risks and test signals: catches false success on missing sources, accidental overwrite/reject mismatch, partial directory movement, lost nested ancestors, creation under file keys, destination parent handling mistakes, and content corruption after rename. Concurrent rename and open-stream rename are covered elsewhere, not here.
