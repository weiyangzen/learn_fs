# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/list_dir_test.go

Purpose: Tests recursive directory listing shape and confirms direct I/O reads still work after listing a directory.

Important APIs/types/functions: `createDirectoryStructureForTest` builds a fixed tree with files, subdirectories, and an empty subdir. `TestListDirectoryRecursively` walks the tree with `filepath.WalkDir` and validates `os.ReadDir` entries at each level. `TestReadFileWorksAfterListDir` creates a GCS object directly with `client.SetupFileInTestDirectory`, lists the mounted directory, then opens the file with `syscall.O_DIRECT` and reads via `operations.ReadFileSequentially`.

Control flow: listing test validates root, parent, child, and empty-directory counts and names. The read-after-list test ensures directory listing/cache activity does not poison later file open/read.

State/persistence: Directory fixtures are created in the bucket-backed test prefix. The second test writes through the storage client and reads through gcsfuse, exercising cross-client visibility.

Dependencies/integration: Uses internal `util.MiB`, storage client globals from `operations_test.go`, setup/client/operations helpers, and testify `require`.

Risks/test signals: ReadDir ordering is assumed. The second test is a regression signal for interactions between list cache/prefetch and direct file reads.
