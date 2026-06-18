# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mman.h

Purpose: Defines memory mapping protections, mapping flags, mmap/mprotect/msync/mlock/shm/madvise/memcntl/meminfo APIs, and mmapobj result structures.

Key definitions:
- Protections: `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, `PROT_NONE`; kernel-only `PROT_USER`, `PROT_ALL`.
- Mapping types/flags: `MAP_SHARED`, `MAP_PRIVATE`, `MAP_FIXED`, `MAP_NORESERVE`, `MAP_ANON`, `MAP_ALIGN`, `MAP_TEXT`, `MAP_INITDATA`, `_MAP_LOW32`, `_MAP_NEW`.
- mmapobj flags: `MMOBJ_PADDING`, `MMOBJ_INTERPRET`; result flags `MR_PADDING`, `MR_HDR_ELF`, kernel-only `MR_RESV`.
- `mmapobj_result_t` and 32-bit variant.
- `memcntl_mha`, `meminfo_t`, 32-bit variants.
- Advice, msync, mlockall, memcntl command, HAT advise, and meminfo request constants.

Key APIs:
- Standard: `mmap()`, `munmap()`, `mprotect()`, `msync()`.
- Large-file variants through feature-test remapping.
- Realtime/POSIX: `mlock()`, `munlock()`, `mlockall()`, `munlockall()`, `shm_open()`, `shm_unlink()`, `posix_madvise()`.
- illumos extensions: `mincore()`, `memcntl()`, `madvise()`, `getpagesizes()`, `mmapobj()`, `meminfo()`.

Important details:
- Feature-test guards are carefully documented because this header has a long compatibility history.
- `_MAP_NEW` preserves backward object compatibility for old mmap return semantics.
- `mmapobj_result_t` records both mapping size and file size so ELF/object mappings can describe padding and header placement.

Relevance to subset A: Highly relevant VM/filesystem boundary ABI because file-backed mappings, object mapping, page advice, locking, and sync behavior interact with VFS and vnode operations.
