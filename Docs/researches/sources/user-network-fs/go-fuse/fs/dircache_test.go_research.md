# sources/user-network-fs/go-fuse/fs/dircache_test.go

Purpose: verifies `FOPEN_CACHE_DIR` directory caching behavior.

Important types/functions: `dirCacheTestNode` counts open calls and reads that occur after the first open. `OpendirHandle` builds 1024 deterministic entries, wraps them in `countingReaddirenter`, and returns `fuse.FOPEN_CACHE_DIR`. `TestDirCacheFlag` reads directory entries twice through `NewLoopbackDirStream`, compares results, and expects two opens but zero cached second-open read callbacks when kernel directory caching works.

State/dependencies: mutex-protected counters and kernel support for FUSE protocol 7.28 directory caching.

Risks/test signals: skips on kernels without required support. The test is sensitive to kernel cache behavior and `DisableReadDirPlus`.
