## sources/sync-backup/kopia/fs/localfs/localfs_benchmark_test.go

Purpose: benchmarks directory iteration cost over directories of varying sizes.

Important APIs/types/functions: `BenchmarkReadDir0`, `BenchmarkReadDir1`, `BenchmarkReadDir2`, `BenchmarkReadDir10`, `BenchmarkReadDir100`, `BenchmarkReadDir1000`, `BenchmarkReadDir10000`, and `benchmarkReadDirWithCount`.

Control flow, state, and persistence: each benchmark creates a temp directory with random UUID filenames, then repeatedly opens it through `localfs.Directory` and iterates entries through `fs.IterateEntries`.

Dependencies and integration points: exercises `filesystemDirectoryIterator`, batching size, object pools, and OS directory operations under benchmark conditions.

Risks and test signals: useful for detecting performance regressions in traversal, batching, and allocation behavior. It does not assert correctness beyond successful iteration.
