# File Research: sources/os/linux/linux-stable/fs/iomap/swapfile.c

Implements generic swapfile activation for iomap filesystems.

Key paths:
- `iomap_swapfile_activate()` fsyncs the file, iterates the whole page-aligned file with `IOMAP_REPORT`, accumulates usable extents, and fills `swap_info_struct`.
- `iomap_swapfile_iter()` accepts only mapped or unwritten extents, rejects inline, holes, dirty metadata, shared extents, and extents outside the swap device.
- `iomap_swapfile_add_extent()` trims physical ranges to page boundaries, accounts for the header page, tracks lowest/highest physical pages, and calls `add_swap_extent()`.
- `iomap_swapfile_fail()` reports path-qualified activation failures.

Important invariants:
- Swap extents must be physically contiguous, page-aligned, committed, non-shared, and on the main swap block device.
- Logical file offsets do not matter to swap once physical page extents are reported.
- A swapfile with no usable page-aligned range is rejected.
