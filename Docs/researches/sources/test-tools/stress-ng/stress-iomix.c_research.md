# sources/test-tools/stress-ng/stress-iomix.c

Purpose: implements the `iomix` stressor, a mixed filesystem I/O workload that creates one temporary backing file per worker instance, preallocates it, unlinks it, then forks one child per available I/O behavior to hammer the same open file descriptor with reads, writes, mmap writes, syncs, inode-flag ioctls, cache operations, copy helpers, sendfile, cachestat, and readahead where supported.

Important APIs/types/functions: `stress_iomix_func` defines child workload functions; `stress_iomix_rnd_offset()` selects random file offsets; `stress_iomix_fsync_min_1Hz()` throttles `fsync`, `fdatasync`, and `sync`; `iomix_funcs[]` is the fan-out table. File APIs include `open`, `fallocate`, `lseek`, `read`, `write`, `mmap`, `msync`, `posix_fadvise`, `sync_file_range`, `copy_file_range`, `sendfile`, `readahead`, `ioctl(FS_IOC_*FLAGS)`, and the Linux `cachestat` syscall wrapper when available.

Control flow: `stress_iomix()` installs a SIGCHLD handler, mmaps shared child PID records, creates a shared bogo counter lock, resolves `iomix-bytes`, creates a temp directory and unlinked temp file, shrinks allocation on `EFBIG` or `ENOSPC`, then forks up to `SIZEOF_ARRAY(iomix_funcs)` children. Each child waits on stress-ng sync start, applies scheduler settings, runs its assigned I/O loop, and exits. The parent waits in `pause()` while the shared bogo counter remains below the stop condition, then kills and reaps children and removes resources.

State and persistence behavior: persistent filesystem state is intentionally temporary and unlinked; the live file survives only by descriptor reference. Runtime state is the shared fd offset, child PIDs in shared mmap, and the global `counter_lock`. Some child functions mutate file contents, inode flags, cache state, and file-cache hints; all should be discarded when the fd and temp directory are cleaned.

Dependencies and integration points: depends heavily on stress-ng filesystem, mmap, sync, signal, lock, random, and kill helpers. Compile-time feature gates tailor the workload to libc, kernel, and filesystem support. Registered as `CLASS_FILESYSTEM | CLASS_OS`, with `iomix-bytes` option and always-on verification.

Risks: children share a single file descriptor, so file offset races are part of the stress model. Filesystems may reject inode flags or preallocation; the code handles space exhaustion but treats many unexpected syscall failures as stressor failures. The mmap path uses `MAP_SHARED | MAP_ANONYMOUS` with a file descriptor, which is platform-sensitive. Cache dropping can block without sufficient privileges.

Test signals: run with multiple workers and `--verify`, vary `--iomix-bytes`, and cover low-space filesystems. Useful pass signals are no stale temp directories, all child PIDs reaped, no unexpected read/write/lseek/fallocate errors, bogo progress from multiple child workloads, and stable behavior on kernels with and without optional syscalls.
