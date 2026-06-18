# File Research: sources/os/bsd/freebsd-src/sys/sys/mman.h

Defines memory mapping, protection, advisory, locking, shared memory, memfd, and kernel `shmfd` ABI/state.

Key content:
- Defines inheritance constants for `minherit`.
- Protection flags: none/read/write/exec plus CHERI bits and max-protection encoding helpers under BSD visibility.
- Mapping flags include shared/private, fixed, semaphore, stack, nosync, anon, guard, excl, nocore, prefault read, low 32-bit, and alignment/superpage alignment.
- Shared memory rename flags support no-replace and exchange.
- Memory locking flags: `MCL_CURRENT`, `MCL_FUTURE`.
- `MAP_FAILED`, `msync` flags, and `madvise`/POSIX madvise constants.
- `mincore` result bits include incore, referenced/modified by self/others, and superpage page-size index.
- Defines `SHM_ANON`, `shm_open2` flags, largepage allocation policies, `struct shm_largepage_conf`.
- Defines `memfd_create` flags and hugepage size encodings.
- Declares `mode_t`, `off_t`, and `size_t` when needed.
- Kernel or `_WANT_FILE` exposes `struct shmfd`: size, VM object, pages, refs, uid/gid/mode, kmapping count, timestamps, inode, MAC label, path, range lock, mutex, flags, seals, and largepage config.
- Kernel declares shm map/unmap/access/alloc/hold/drop/truncate/largepage/remove-prison/path APIs and `shm_ops`.
- Userland declares mmap-family, mlock-family, shm, memfd, and largepage shm APIs.

Research relevance:
- Filesystems and VFS interact with memory mapping through file ops, vnode-backed mappings, shared memory fileops, and `mmap` flags.
- `struct shmfd` is a kernel file-like object with stat-compatible metadata and MAC labeling.
- Largepage and memfd behavior can affect VM/filesystem tests.

Cautions:
- Many constants are gated by feature visibility macros.
- Some POSIX typed memory APIs are explicitly noted as missing.
