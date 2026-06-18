# File Research: sources/os/linux/linux/mm/memfd.c

## Role

Implementation of the `memfd_create()` syscall and shared memfd sealing support for tmpfs/shmem and hugetlbfs-backed anonymous files. It creates anonymous in-memory files, validates memfd flags and noexec policy, manages seal addition/querying through `fcntl()`, checks mmap writability against write seals, and provides a folio allocation helper for GUP-based memfd pinning.

## Key Behavior

- Reuses `PAGECACHE_TAG_TOWRITE` as `MEMFD_TAG_PINNED` for tmpfs/hugetlbfs pin scanning because these memory-only filesystems do not use that tag for writeback.
- Detects potentially pinned folios by comparing actual folio references with the expected page-cache reference count after draining local LRU additions.
- `memfd_wait_for_pins()` tags folios with extra refs, drains all LRU additions once, then performs bounded retry scans with killable sleeps; it clears tags as pins disappear and returns `-EBUSY` if folios remain pinned on the final scan.
- `memfd_alloc_folio()` allocates missing folios for memfd pinning: shmem uses `shmem_read_folio()`, while hugetlbfs reserves one hugepage, allocates from non-highmem/non-movable zones, zeroes it, marks it uptodate, serializes insertion with the hugetlb fault mutex, adds it to the page cache, sets subpool metadata, and unwinds reservations on failure.
- `memfd_add_seals()` validates write mode and seal bits, rejects additions after `F_SEAL_SEAL`, expands `F_SEAL_EXEC` on executable files into shrink/grow/write/future-write seals, denies writable mappings before adding `F_SEAL_WRITE`, waits for outstanding pins, and then ORs new seals into the inode seal word.
- `memfd_get_seals()` and `memfd_fcntl()` implement `F_GET_SEALS` and `F_ADD_SEALS` for supported shmem or hugetlbfs files.
- `check_sysctl_memfd_noexec()` applies per-pid-namespace `vm.memfd_noexec` policy by defaulting unspecified exec flags to `MFD_NOEXEC_SEAL` or `MFD_EXEC`, and can reject executable memfds when noexec is enforced.
- `memfd_check_seals_mmap()` blocks new writable shared mappings under write/future-write seals and strips `VM_MAYWRITE` from read-only shared mappings so later `mprotect(PROT_WRITE)` cannot bypass sealing.
- `sanitize_flags()` validates memfd creation flags, permits hugepage size encodings only with `MFD_HUGETLB`, rejects simultaneous `MFD_EXEC` and `MFD_NOEXEC_SEAL`, then applies sysctl noexec policy.
- `alloc_name()` constructs the internal `memfd:<user-name>` name with `NAME_MAX` bounds and user-copy error handling.
- `memfd_alloc_file()` creates either a shmem or hugetlb anonymous file, initializes anonymous inode security, sets seek/read/write file modes and `O_LARGEFILE`, clears default `F_SEAL_SEAL` when sealing is allowed, and applies noexec mode plus `F_SEAL_EXEC` for `MFD_NOEXEC_SEAL`.
- `SYSCALL_DEFINE2(memfd_create)` validates flags, copies the name, maps `MFD_CLOEXEC` to `O_CLOEXEC`, and returns a new fd for the allocated file.

## Dependencies

Uses VFS/file allocation, shmem, hugetlbfs, page cache XArray scanning, folios, GUP pinning support, LRU drain helpers, `fcntl` seal constants, pid namespace sysctl policy, anonymous inode LSM initialization, syscall fd installation, and `uapi/linux/memfd.h`.

## Research Notes

The key safety path is adding `F_SEAL_WRITE`: the caller must prevent new writable references, then this file denies writable mappings and waits for elevated folio refs that may represent DMA or GUP pins. The noexec policy is enforced at creation time, while mmap checks enforce write seals after creation. Hugetlb folio allocation is careful about reservations, zeroing, uptodate state, and page-cache serialization because it supports long-term pinned use cases outside the usual fault path.
