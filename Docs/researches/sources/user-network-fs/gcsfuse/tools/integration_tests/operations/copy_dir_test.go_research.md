# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_dir_test.go

Purpose: Exercises recursive directory copy behavior through a mounted GCSFuse filesystem for populated and empty source directories copied into nonexistent, empty, and non-empty destinations.

Important APIs/types/functions: `createSrcDirectoryWithObjects` builds `srcCopyDir` with one file and one subdir; `checkIfCopiedDirectoryHasCorrectData` validates entry count, entry names/types, and copied file content; `createDestNonEmptyDirectory` creates a destination with a pre-existing subdirectory; `checkIfCopiedEmptyDirectoryHasNoData` verifies empty copies. Test functions call `operations.CopyDir`, `os.ReadDir`, `os.Mkdir`, `operations.WriteFile`, and `operations.ReadFile`.

Control flow: each test creates an isolated operations test directory, prepares source/destination layouts, invokes `CopyDir`, then validates exact resulting directory shape. When copying into an existing directory, the source directory itself becomes a child; when copying into a nonexistent path, the destination path is created as the copied tree.

State/persistence: Files and explicit directory marker behavior are observed via the mounted filesystem. Existing destination entries are expected to survive unchanged. Test data persists in the shared operations test prefix until package cleanup.

Dependencies/integration: Relies on constants from `operations_test.go` and helper functions from `util/operations` and `util/setup`.

Risks/test signals: The tests assume `os.ReadDir` ordering matches lexical ordering of expected names. A passing run signals that copy preserves file contents, explicit empty directories, and existing destination contents across all configured mount modes.
