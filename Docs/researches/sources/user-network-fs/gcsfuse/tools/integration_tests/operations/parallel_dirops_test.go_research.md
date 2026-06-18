# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/parallel_dirops_test.go

Purpose: Stress-tests concurrent directory operations, lookup, readdir, delete, rename, and mkdir paths when parallel directory operations are allowed.

Important APIs/types/functions: `testDirStrucure` records randomized fixture names. `createDirStructure` creates two explicit dirs and several files with fixed sizes. `deleteDirStructure` calls `setup.CleanUpDir`. `lookUpFileStat` wraps `os.Stat` for goroutines. Tests use `sync.WaitGroup`, `os.ReadDir`, `filepath.WalkDir`, `os.RemoveAll`, `os.Remove`, `os.Rename`, `os.Mkdir`, and testify assertions.

Control flow: each test creates a fresh randomized tree, launches concurrent operations, waits, then validates either deterministic success for independent operations or accepted race outcomes for lookup versus mutation. Race tests allow lookup to succeed before mutation or fail with not-exist after mutation.

State/persistence: Fixture state is mounted-directory state backed by GCS objects. Cleanup removes the entire randomized test directory. Concurrent tests intentionally create transitional states and then assert final persisted state.

Dependencies/integration: Uses common setup/operations helpers and standard filesystem calls.

Risks/test signals: Some assertions assume lexical order of directory entries. Shared local variables are written by goroutines but each variable is assigned by one goroutine before `Wait`, limiting data-race risk. Passing signals directory operation concurrency preserves correctness and tolerates expected races.
