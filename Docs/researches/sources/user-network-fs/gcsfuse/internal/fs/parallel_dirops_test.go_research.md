# sources/user-network-fs/gcsfuse/internal/fs/parallel_dirops_test.go

Purpose: tests filesystem behavior when parallel directory operations (`readdir` and lookup) are enabled. It verifies that concurrent lookups, listings, creates, deletes, mkdirs, and renames produce valid outcomes with and without metadata caches.

Important APIs/types: `ParallelDiropsTest` embeds `fsTest`; `ParallelDiropsWithoutCachesTest` embeds it and reruns the same tests with `DirTypeCacheTTL` and `InodeAttributeCacheTTL` set to zero. Setup enables implicit directories, sets `DisableParallelDirops: false`, configures rename limit and noop metrics/tracing, and creates a bucket structure with root files, an explicit directory with files, and an implicit directory.

Control flow and state: simple parallel tests perform two simultaneous `os.Stat` calls for the same file or directory, two `os.ReadDir` calls for explicit/implicit directories, and mixed parent/child readdir. Mutation races pair lookup/read-dir with `os.Create`, `os.Mkdir`, `os.Remove`, `os.RemoveAll`, and `os.Rename` on the same path. Assertions allow either valid ordering: lookup/list may see the old state or may get `os.IsNotExist`, while the mutating operation must succeed and final state is checked.

Dependencies and integration: uses mounted filesystem operations, fake GCS object setup, `sync.WaitGroup`, `os`, `path`, `cfg`, and testify assertions. It exercises the actual directory-operation locking and cache interaction in the mounted server rather than direct method calls.

Risks: the concurrency is only two goroutines per scenario and does not loop heavily, so rare races may escape. It assumes specific listing order for initial structure. Some assertions use `assert.Contains(filePath, stat.Name())`, which is permissive and mostly checks basename inclusion.

Test signals: protects against deadlocks and invalid state transitions introduced by parallel dirops, especially when caches are disabled and lookups/listings must consult backing storage more often.
