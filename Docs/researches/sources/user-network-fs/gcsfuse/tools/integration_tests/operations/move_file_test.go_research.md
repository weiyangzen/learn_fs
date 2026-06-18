# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/move_file_test.go

Purpose: Verifies move/rename-like file relocation within the same directory tree, across directories, and over an existing destination file.

Important APIs/types/functions: `createSrcDirectoryAndFile` creates a source directory and writes `MoveFileContent`; `checkIfFileMoveOperationSucceeded` calls `operations.Move` and validates destination content; tests use `os.Mkdir`, `operations.CreateFileWithContent`, `setup.CompareFileContents`, and testify assertions.

Control flow: same-directory and different-directory tests create source file and destination directory, invoke the shared move helper, and read the moved file. The existing-destination test creates both source and destination files, moves source onto destination, checks overwritten content, then asserts the source path is gone.

State/persistence: Moves modify GCS object names through the mount. The overwrite case validates replacement semantics and removal of the old object.

Dependencies/integration: Uses operation constants from `operations_test.go`, setup permissions, helper operation wrappers, and testify.

Risks/test signals: The source-removed check uses string matching for "no such file or directory". Passing signals file rename/copy-delete semantics are consistent for normal and overwrite moves.
