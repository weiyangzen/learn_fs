# File Research: sources/os/bsd/netbsd-src/sys/sys/mman.h

Public memory-mapping API header. It defines protection bits, PaX `PROT_MPROTECT` helpers, mapping sharing/options/type/alignment flags, `MAP_FMT`, `MAP_FAILED`, msync/mlockall flags, POSIX and NetBSD madvise values, minherit modes, memfd flags, and userland prototypes for mmap/munmap/mprotect/msync/mlock/munlock/mlockall/munlockall/madvise/mincore/minherit/mremap/memfd_create/posix_madvise/shm_open/shm_unlink.

Filesystem relevance is high through file-backed mappings, shared memory, memfd, and UVM integration. Risks include flag ABI stability, alignment encoding, PaX protection semantics, and feature-test conditional exposure.
