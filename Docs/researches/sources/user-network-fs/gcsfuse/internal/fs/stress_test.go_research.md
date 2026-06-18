<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go

Purpose: concurrency stress tests for common filesystem operations through the mounted gcsfuse filesystem.

Important APIs/types/functions: helper `forEachName`; ogletest suite `StressTest`; tests `CreateAndReadManyFilesInParallel`, `TruncateFileManyTimesInParallel`, `CreateInParallel_NoTruncate`, `CreateInParallel_Truncate`, `CreateInParallel_Exclusive`, `MkdirInParallel`, and `SymlinkInParallel`.

Control flow: `forEachName` fans work out to 8 goroutines and returns the first error. The first stress test writes 32 files in parallel and reads them back. The truncate test shares one file among 16 workers repeatedly truncating to random sizes for 500 ms, then verifies the final size matches one worker's final truncate. Other cases delegate to `fusetesting` parallel create/mkdir/symlink tests.

State and persistence behavior: stresses local in-memory inode/handle state, synchronization, and eventual fake GCS object state under parallel operations. The truncate test checks visible metadata consistency rather than object content.

Dependencies and integration points: uses Go runtime parallelism, `errgroup`, `fusetesting` helpers, and the shared fs test mount.

Risks: these tests can expose races, deadlocks, non-atomic truncate state, duplicate create handling, and symlink/mkdir interleaving bugs. Random truncation means failures may be timing-dependent.

Test signals: parallel create/read content consistency, concurrent truncate final-size coherence, and standard FUSE parallel operation suites for create, exclusive create, mkdir, and symlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go -->
