# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem.h

Public memory allocation API for libnvme.

Key declarations:
- `libnvme_alloc(size_t len)` for zero-initialized libnvme-compatible allocation.
- `libnvme_realloc(void *p, size_t len)` preserving old contents and zero-initializing newly allocated portions.
- `libnvme_free(void *p)`.
- `struct libnvme_mem_huge`, containing:
  - allocation length
  - whether allocation came from libnvme heap allocator
  - pointer
- `libnvme_alloc_huge()` and `libnvme_free_huge()`.

Research notes:
- The header abstracts platform differences between POSIX aligned allocation/mmap and Windows aligned heap/VirtualAlloc.
- Callers must retain the huge allocation descriptor for correct cleanup.
