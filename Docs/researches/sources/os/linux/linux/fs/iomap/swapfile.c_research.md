# File Research: sources/os/linux/linux/fs/iomap/swapfile.c

Implements swapfile activation for filesystems that expose physical extents through iomap.

Key structure:
- `struct iomap_swapfile_info` accumulates physically contiguous mappings, tracks usable page ranges, extent count, and the target `swap_info_struct`.

Main flow:
- `iomap_swapfile_activate()` fsyncs the file first so mappings are committed, iterates the page-aligned file size with `IOMAP_REPORT`, validates mappings, adds the final accumulated extent, rejects files with no usable page, and fills `pagespan`, `sis->max`, and `sis->pages`.
- `iomap_swapfile_iter()` accepts only `IOMAP_MAPPED` or `IOMAP_UNWRITTEN`; rejects inline, holes, dirty/uncommitted metadata, shared extents, and mappings outside the swap device.
- Adjacent physical iomaps are merged before being reported.
- `iomap_swapfile_add_extent()` rounds physical starts up and ends down to page boundaries, skips too-short extents, accounts for the swap header page, updates lowest/highest physical page, and calls `add_swap_extent()`.

This file is strict because swap requires stable, non-shared, page-aligned physical storage.
