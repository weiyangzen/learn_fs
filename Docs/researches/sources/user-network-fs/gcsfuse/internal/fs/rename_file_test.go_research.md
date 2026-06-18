<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go

Purpose: integration coverage for file rename semantics, including missing source, replacing an existing destination, same-parent and cross-parent moves, and symlink renames.

Important APIs/types/functions: testify suite `RenameFileTests`; tests `TestRenameFileWithSrcFileDoesNotExist`, `TestRenameFileWithDstDestFileExist`, `TestRenameFile`, and `TestRenameSymlinkToFile`.

Control flow: tests stat fixtures, call `os.Rename`, verify old-path `ENOENT`, verify new path attributes and content, and use `os.Lstat`/`os.Readlink` for symlink preservation.

State and persistence behavior: object namespace state changes in the fake bucket and inode mappings should follow the new name. Destination replacement must expose source content. Symlink rename should move the link object itself rather than the target.

Dependencies and integration points: exercises `fileSystem.Rename` file path, object rewrite/atomic rename behavior depending on bucket type, inode cache refresh, and symlink inode handling.

Risks: rename-over-existing is easy to mishandle with stale destination inodes or cache entries. Symlink rename requires not dereferencing the link. Cross-parent moves need parent directory cache invalidation on both sides.

Test signals: missing source error, destination replacement content, same and different parent moves, old path disappearance, new path stat/read correctness, and symlink target preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go -->
