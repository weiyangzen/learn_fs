# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_file_test.go

Purpose: Tests normal file rename, error behavior for missing sources, and symlink rename behavior.

Important APIs/types/functions: `TestRenameFile` uses `operations.RenameFile` and content comparison. `TestRenameFileWithSrcFileDoesNoExist` checks missing-source errors. `TestRenameSymlinkToFile` uses `os.WriteFile`, `os.Symlink`, `os.Rename`, `os.Lstat`, `os.Readlink`, and `operations.ReadFile`.

Control flow: the normal test creates a file, reads content, renames, and validates content at the new path. The missing-source test expects an error containing no-such-file. The symlink test creates a target file and symlink, renames the symlink path, verifies the old symlink is gone, the new path remains a symlink to the same target, and reading through it returns target content.

State/persistence: File object, symlink inode representation, and rename metadata are all exercised through the mount.

Dependencies/integration: Uses operation/setup helpers and testify `assert`/`require`.

Risks/test signals: Symlink support must be enabled/available in the tested mount configuration. Passing signals rename preserves file content and symlink identity while surfacing expected errors.
