# File Research: sources/os/linux/linux/mm/mincore.c

## Role

`mincore.c` implements the `mincore(2)` system call, reporting whether pages in a process virtual address range are resident enough that access would not require page-in I/O at the time of inspection.

## Main Responsibilities

- Validate user arguments for alignment, address range access, and output vector access.
- Walk VMAs page-table-by-page-table and fill a byte vector with residency bits.
- Check page cache residency for unmapped file-backed ranges.
- Handle shmem swap-cache entries, regular swap entries, migration entries, hwpoison-like non-swap entries, THPs, and hugetlb mappings.
- Restrict file-backed page-cache disclosure to avoid side-channel leakage.

## Key Entry Points

- `SYSCALL_DEFINE3(mincore, ...)`: syscall wrapper, temporary page-sized vector allocation, chunked walk/copy loop.
- `do_mincore()`: resolves the VMA, applies `can_do_mincore()`, and walks the requested subrange.
- `mincore_pte_range()`: PMD/PTE walker for normal mappings.
- `mincore_unmapped_range()` and `__mincore_unmapped_range()`: page-cache lookup for unmapped file-backed areas or zero fill for anonymous gaps.
- `mincore_hugetlb()`: hugepage-specific walker.
- `mincore_page()`: page-cache/xarray residency lookup.
- `mincore_swap()`: swap-cache residency lookup.

## Residency Semantics

Present PTEs and PMD-mapped THPs are reported resident. PTE holes in file VMAs are checked against the backing mapping at the corresponding file offset; holes in anonymous VMAs are reported not resident. Page-cache entries are resident only if they refer to an uptodate folio. Xarray value entries in shmem mappings are interpreted as swap entries and checked via swap cache.

Non-swap special entries in page tables, such as migration or hwpoison entries, are treated as resident for non-shmem PTE checks. Hugetlb mappings are reported resident unless the huge PTE is none or a marker.

## Security Gate

`can_do_mincore()` allows anonymous VMAs and file mappings whose inode owner/capability check or write permission check would permit page-cache disclosure. For disallowed non-anonymous file-backed mappings, `do_mincore()` fills the result range with resident bits rather than exposing real cache state.

## Concurrency

The syscall holds `mmap_read_lock()` per chunk and the page-table walker uses `PGWALK_RDLOCK`. PTE reads happen under page-table locks. Shmem swap lookups grab the swap device around `swap_cache_get_folio()` because the mapping lookup is lockless.

## Error Handling

Invalid alignment returns `-EINVAL`; invalid address range access returns `-ENOMEM`; invalid output vector access returns `-EFAULT`; temporary buffer allocation failure returns `-EAGAIN`; missing VMAs during the walk return `-ENOMEM`. Results may become stale immediately after return unless the caller has locked memory.
