# sources/test-tools/stress-ng/stress-tmpfs.c

## Purpose
Implements the `tmpfs` stressor, which finds a writable tmpfs mount, creates an unlinked sparse file sized from available tmpfs space, and repeatedly maps, touches, syncs, unmaps, and remaps its pages to stress tmpfs-backed VM behavior.

## Important APIs, Types, And Functions
`mapping_info_t` stores per-page address and mapping state. `stress_tmpfs_context_t` passes file descriptor and size to the OOMable child. `stress_tmpfs_open()` scans mounts with `stress_mount_get()`, filters to tmpfs using `statfs()` and `TMPFS_MAGIC`, avoids sensitive mount prefixes, creates an unlinked temp file, and extends it to a page-aligned capped size. `stress_tmpfs_child()` performs the mmap/madvise/mincore/msync/xattr/unmap/remap workload. `stress_tmpfs()` opens the tmpfs file and runs the child under `stress_oomable_child()`.

## Control Flow
The child allocates a `mapping_info_t` array for every page in the tmpfs file, resolves `tmpfs-mmap-async` and `tmpfs-mmap-file`, and loops while running. Each iteration does random file reads/writes, optional xattr set/remove probes, `fsync()`, and a full-file shared mmap with optional random mmap flags such as hugepage, nonblock, or locked mappings. It may disable problematic populate/hugetlb flags after mmap failures. Once mapped, it optionally writes and `msync()`s the whole file, randomizes advice, touches pages with mincore helpers, writes verification data, optionally verifies it, then unmaps all pages in random order. If `MAP_FIXED` is available, it maps individual pages back in random order at original addresses, touches/advises/verifies them, optionally writes/syncs file-backed data, and finally unmaps all mapped pages.

## State And Persistence Behavior
The temp file is unlinked immediately and closed in both child and parent paths, so tmpfs space should be reclaimed even if the child exits early. Runtime state is the fd, per-page heap array, mappings, and xattrs that are removed if successfully created. No named file should persist.

## Dependencies And Integration Points
The stressor requires `sys/vfs.h` and `statfs()`. It uses stress-ng mount discovery, mmap, madvise, mincore, OOMable child, temp-file, memory, and optional xattr helpers. Options are `tmpfs-mmap-async` and `tmpfs-mmap-file`; verification is optional. It registers as `CLASS_MEMORY | CLASS_VM | CLASS_OS`.

## Risks And Test Signals
Tmpfs capacity can change under load; mmap failures are retried up to `NO_MEM_RETRIES_MAX`, and excessive failures stop the loop. `MAP_FIXED` remapping may fail and is tracked per page. Optional verification catches data pattern mismatches after mmap writes. Test signals include skip when no writable tmpfs is found, bogo increments per map/unmap cycle, optional verification failures, no persistent temp files, and successful cleanup after OOMable child exit.
