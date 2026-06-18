# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/file_and_dir_attributes_test.go

Purpose: Verifies stat attributes for files, empty directories, and non-empty directories, focusing on name, size, and modification-time windows.

Important APIs/types/functions: constants define retry timing, byte expectations, and directory/file counts. `checkIfObjectAttrIsCorrect` wraps `os.Stat` and validates mounted path name, modtime range, and size. `TestFileAttributes`, `TestEmptyDirAttributes`, and `TestNonEmptyDirAttributes` run the check inside `operations.RetryUntil`.

Control flow: each test creates a randomized object/directory while capturing pre/post timestamps adjusted by `operations.TimeSlop`, then retries until stat attributes match or timeout.

State/persistence: Created objects/directories persist in the mounted test prefix. Directory size is expected to be zero regardless of contained files; file size is expected to match the known content length.

Dependencies/integration: Uses `context`, time handling, setup and operation helpers, and shared `DirForOperationTests`.

Risks/test signals: Attribute timing is sensitive to kernel/GCS clock differences, mitigated by slop and retry. Passing signals stable stat metadata projection for both object and directory inodes.
