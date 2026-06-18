# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_dir_test.go

Purpose: Regression test for renaming a source directory onto a non-empty destination directory and preserving filesystem health after the failed operation.

Important APIs/types/functions: `TestRenameDirToNonEmptyDestDirectory` uses `os.Mkdir`, `operations.CreateFileWithContent`, `os.Rename`, `os.Stat`, `os.Remove`, and testify assertions.

Control flow: the test creates empty `srcDir`, non-empty `destDir/file.txt`, attempts `os.Rename(srcDir, destDir)`, asserts an error mentioning file-exists/not-empty, stats both source and destination to verify they remain usable, then deletes the destination file and both directories.

State/persistence: The failed rename should leave both directory markers and destination file intact. Cleanup validates that no poisoned local/mounted state prevents subsequent remove operations.

Dependencies/integration: Uses operations/setup helpers and standard POSIX calls through the mount.

Risks/test signals: Error message matching allows several platform-specific substrings but is still string-dependent. Passing signals failed directory rename cleanup is correct and addresses the linked regression context in comments.
