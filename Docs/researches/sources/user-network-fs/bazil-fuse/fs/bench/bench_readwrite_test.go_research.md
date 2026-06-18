<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go -->
# sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go

Purpose: benchmarks FUSE read, write, and write+sync paths for page-cache and direct-I/O modes at several transfer sizes.

Important APIs, types, and functions: defines `benchFS`, `benchDir`, `benchFile`, `benchConfig`, `benchmark`, `benchmarkSizes`, helper functions `doBenchWrite`, `doBenchWriteSync`, and `doBenchRead`. File handlers implement `Open`, `Read`, `Write`, and `Fsync`.

Control flow: each benchmark mounts the test FS with large readahead, async read, and writeback cache, spawns a helper, then the helper performs the requested I/O loop.

State and persistence behavior: file content is synthetic; reads fill response capacity, writes acknowledge byte counts, and no durable backing store exists.

Dependencies and integration points: uses FUSE open flags `OpenDirectIO` and `OpenKeepCache`, fstestutil, spawntest, and Go benchmark subtests.

Risks and test signals: `doBenchRead` opens with `os.Create`, so benchmark semantics rely on FUSE read behavior for the resulting descriptor. Timing is sensitive to kernel cache options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/bench/bench_readwrite_test.go -->
