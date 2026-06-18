# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-linux.c

Linux memory allocation helpers for libnvme.

Key behavior:
- `libnvme_alloc()` page-aligns allocation size to 4 KiB, uses `posix_memalign()` with system page size alignment, and zeroes the buffer.
- `libnvme_realloc()` allocates a fresh aligned buffer, copies up to `min(old_len, len)` using `malloc_usable_size()`, and frees the old pointer on success.
- `libnvme_free()` wraps `free()`.
- `libnvme_alloc_huge()`:
  - Uses normal aligned allocation for buffers smaller than `HUGE_MIN` (`0x80000`).
  - Tries `mmap(... MAP_HUGETLB ...)` for larger allocations.
  - Falls back to 2 MiB-aligned `posix_memalign()` plus `madvise(... MADV_HUGEPAGE ...)`.
- `libnvme_free_huge()` frees either heap-backed allocation or `munmap()`s huge-page mapping based on descriptor metadata.

Research notes:
- The huge allocation descriptor records whether cleanup should use `free()` or `munmap()`.
- `libnvme_realloc()` preserves the original buffer on allocation failure.
