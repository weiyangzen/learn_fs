# sources/test-tools/stress-ng/stress-fiemap.c

Purpose: implements `fiemap`, which stresses the Linux `FS_IOC_FIEMAP` ioctl while another process mutates file extents by writing sparse data and punching holes.

Important APIs/types/functions: `stress_fiemap_writer()` writes one-byte records at random 8 KiB-aligned offsets and optionally punches 8 KiB holes with `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`. `stress_fiemap_ioctl()` first asks the kernel for mapped extent count, reallocates a `struct fiemap` large enough for those extents, and issues a second ioctl to fetch them. `stress_fiemap_spawn()` forks ioctl workers synchronized with the parent. A global `counter_lock` serializes bogo counter updates across processes.

Control flow: `stress_fiemap()` creates a temp file, unlinks it after open, checks FIEMAP support, spawns up to four ioctl child processes sharing the same fd, synchronizes all workers, then runs the writer loop in the parent. On exit it sends SIGALRM to children, closes the fd, removes the temp dir, unmaps pid storage, and destroys the counter lock.

State and persistence behavior: a temporary sparse file exists only by fd after unlink. Extent mutations persist only for the stressor lifetime. Shared process state is limited to the inherited fd, mapped pid table, and named lock.

Dependencies and integration points: requires `linux/fs.h`, `linux/fiemap.h`, and `FS_IOC_FIEMAP`; otherwise registers unimplemented. Uses stress-ng temp-file, sync-start, kill/wait, file-usage, lock, random, and bogo-lock helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filesystem support varies; `EOPNOTSUPP` is a skip/not-implemented condition. Extent counts can change between the count and fetch ioctls due to the writer, intentionally exercising races. `O_SYNC` changes fdatasync behavior. ENOSPC and EOPNOTSUPP hole-punch responses are handled but reduce mutation coverage.

Test signals: run on ext4, xfs, btrfs, tmpfs, and filesystems without FIEMAP. Validate skip messages for unsupported filesystems, no realloc failures under heavy extent churn, and correct reaping of four child ioctl workers.
