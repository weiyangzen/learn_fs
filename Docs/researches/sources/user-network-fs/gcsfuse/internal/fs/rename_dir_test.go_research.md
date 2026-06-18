<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go

Purpose: integration tests for directory rename semantics across missing sources, non-empty destinations, empty directories, local files, open GCS files, same-parent/different-parent moves, replacement of empty destinations, symlink rename, and path reuse after rename/delete.

Important APIs/types/functions: testify suite `RenameDirTests`; standard `os.Rename`, `os.Stat`, `os.ReadDir`, `os.RemoveAll`, `os.Mkdir`; Python `os.rename` workaround for renaming into an existing empty directory.

Control flow: tests assume fixture directories `foo`, `bar`, nested explicit folders, and files from the shared fs test setup. The rename operation is invoked through the mounted filesystem, followed by old-path stat failure, new-path stat success, directory listing validation, or expected error matching.

State and persistence behavior: rename changes visible namespace state in the fake bucket and local inode maps. The suite also verifies that recreating a directory at an old path after rename produces an empty fresh directory, and that deleting/recreating a parent does not poison later local-file creation at the same path.

Dependencies and integration points: exercises `fileSystem.Rename`, directory inode rename logic, local file tracking, symlink handling, GCS copy/delete or folder rename behavior, directory listing cache invalidation, and error mapping to kernel strings such as `file exists`, `operation not supported`, and `no such file or directory`.

Risks: directory rename is consistency-sensitive because it may move many objects and cached inodes. Open local files in a source directory block rename, while open read-only GCS file handles are allowed but become unusable for writes. Existing empty destination behavior differs between Go helper support and raw syscall behavior.

Test signals: validates missing source failure, non-empty destination failure, empty source move, symlink move, local-open-file rejection, same/different-parent subtree preservation, replacement of empty destination, open GCS file behavior, namespace reuse after rename, and local-file reuse after parent deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go -->
