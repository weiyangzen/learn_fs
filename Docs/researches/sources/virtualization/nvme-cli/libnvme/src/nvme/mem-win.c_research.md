# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mem-win.c

Windows memory allocation helpers matching the public `mem.h` API.

Key behavior:
- Defines a local `getpagesize()` using `GetSystemInfo()`.
- `libnvme_alloc()` rounds to 4 KiB, allocates with `_aligned_malloc()` using system page-size alignment, and zeroes memory.
- `libnvme_realloc()` handles NULL as allocation, determines old size with `_aligned_msize()`, allocates a new aligned buffer, copies preserved data, and frees old memory on success.
- `libnvme_free()` wraps `_aligned_free()`.
- `libnvme_alloc_huge()`:
  - Uses regular aligned allocation below the large-page threshold.
  - Tries `VirtualAlloc(... MEM_LARGE_PAGES ...)` when large pages are available.
  - Falls back to regular `VirtualAlloc()`.
  - Finally falls back to `_aligned_malloc()` with large-page or page-size alignment.
- `libnvme_free_huge()` uses `_aligned_free()` or `VirtualFree()` based on descriptor metadata.

Research notes:
- Large-page allocation requires Windows privilege (`SeLockMemoryPrivilege`), so the fallback chain is important.
- The implementation mirrors Linux metadata semantics: descriptor tells the free path whether the memory is libnvme heap-backed or OS virtual allocation-backed.
