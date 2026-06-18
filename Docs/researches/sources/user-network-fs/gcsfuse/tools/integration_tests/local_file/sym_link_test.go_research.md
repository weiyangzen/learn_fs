<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go

## Purpose

This file tests symlink interactions with local unsynced files: creating and reading symlinks, behavior after deleting the target, and renaming symlinks.

## Important APIs, Types, and Functions

`createAndVerifySymLink` creates a local file, writes unsynced content, creates a symlink via `operations.CreateSymLink`, validates `ReadLink`, and reads through the symlink. Tests use `os.Stat`, `os.Lstat`, `os.Rename`, and GCS validators.

## Control Flow

`TestCreateSymlinkForLocalFile` creates the symlink and closes the target, validating GCS content. `TestReadSymlinkForDeletedLocalFile` removes the target path, closes the unlinked handle without upload, then expects `os.Stat` on the symlink to return not-exist. `TestRenameSymlinkForLocalFile` renames the symlink, verifies the old symlink is gone, verifies the new symlink points to the target and reads content, then closes the target.

## State and Persistence Behavior

Symlink entries are namespace state pointing at local file paths. Removing the target unlinks the local file and prevents later GCS sync; renaming the symlink changes only link path state, not target file state.

## Dependencies and Integration Points

It depends on local-file helpers and shared symlink/readlink/readfile operation validators. It covers POSIX clients that use symlinks to open or move references to in-progress local files.

## Risks and Test Signals

Symlink support can vary by platform/mount configuration. Passing signals are successful read-through before target close, dangling symlink failure after target delete, and preserved link target after symlink rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go -->
