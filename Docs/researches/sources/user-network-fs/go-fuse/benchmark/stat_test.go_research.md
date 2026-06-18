# sources/user-network-fs/go-fuse/benchmark/stat_test.go

Purpose: tests and benchmarks a static in-memory stat/readdir workload and compares it with a libfuse C filesystem.

Important functions: `setupFS` mounts a node and registers cleanup; `TestNewStatFs` verifies constructed directory hierarchy and file mode behavior; `BenchmarkGoFSStat` populates `StatFS` from `testpaths.txt` and shells out to `bulkstat.bin`; `BenchmarkGoFSReaddir` times directory reads; `TestingBOnePass` measures an external stat pass and optionally logs GC data; `BenchmarkLibfuseHighlevelThreadedStat` creates a C `cstatfs` mount and runs the same stat helper.

State/dependencies: uses FUSE mounts, temp files, `bulkstat.bin`, `cstatfs`, `fusermount`, path-list fixtures, and GOMAXPROCS.

Risks/test signals: strong integration coverage of namespace construction and stat scalability; fragile where benchmark binaries or libfuse are absent.
