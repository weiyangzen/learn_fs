# File Research: sources/virtualization/qemu/block/parallels.c

## Purpose
Implements QEMU's Parallels disk image format driver. It supports probing, opening, reading, writing, cluster allocation, discard/zero handling, image creation, image consistency checking/repair, header/BAT flushing, and optional backing files.

## Main Entry Points
- `parallels_probe()` identifies Parallels v2 images with either supported magic string.
- `parallels_open()` parses runtime preallocation options, opens the file child, reads and validates the header/BAT, loads format extensions in read-only mode, marks writable images in-use, builds used-cluster state, and optionally repairs detected issues.
- `parallels_close()` clears the in-use flag, writes the header, truncates tail preallocation/leaks, frees bitmaps/header memory, and removes the migration blocker.
- `parallels_co_readv()` and `parallels_co_writev()` implement sector-based reads and writes through the BAT.
- `parallels_co_block_status()` reports allocated host extents.
- `parallels_co_pdiscard()` and `parallels_co_pwrite_zeroes()` deallocate whole clusters when safe.
- `parallels_co_check()` performs image check/fix operations.
- `parallels_co_create()` and `parallels_co_create_opts()` create a new Parallels image.

## Internal Mechanics
The driver maps guest sectors to host sectors through a block allocation table (`bat_bitmap`). A BAT entry of zero means unallocated. `tracks` is the cluster size in sectors, and `off_multiplier` differs between old and extended magic formats. `block_status()` walks contiguous allocated or unallocated regions and returns the host sector mapping plus the number of sectors covered.

Writes call `allocate_clusters()`, which finds the current status, allocates missing clusters from holes or by extending the file, optionally preallocates extra space, copies data from the backing file for copy-on-write semantics, marks clusters used, updates BAT entries, and advances `data_end`. BAT modifications are tracked in `bat_dirty_bmap`; `parallels_co_flush_to_os()` writes dirty header/BAT blocks back to storage.

The used-cluster bitmap is built from current BAT entries. It is used both for normal allocation and for consistency checking. The check path validates the in-use flag, `data_off`, clusters outside the image, leaked tail space, and duplicate BAT entries. With fix flags, it updates metadata, clears bad entries, reallocates duplicate clusters, truncates leaked space, and collects block-fragmentation statistics.

Image creation writes a v2 header with `HEADER_MAGIC2`, calculated geometry, BAT size, total sectors, and data offset, then zeroes the BAT/data-offset padding area.

## Dependencies
Uses QEMU block coroutines, image creation QAPI visitors, qdict option conversion, bitmap helpers, migration blockers, aligned allocation, and shared Parallels declarations from `parallels.h`. Format extension parsing is delegated to `parallels_read_format_extension()`.

## Filesystem/Block Relevance
This is a sparse COW-capable virtual disk image format. It shows how QEMU maintains a cluster allocation table, performs backing-file copy-on-write, supports hole reuse, handles preallocation, and repairs metadata corruption.

## Risks and Notes
- The driver uses a conservative coroutine mutex around BAT access and image extension.
- Live migration is blocked because the format lacks the needed activation/migration support.
- Discard/zero is only supported for whole clusters and is rejected when a backing file exists, because the format has no explicit zero marker and could expose stale backing data.
- Format extensions are ignored with a warning in writable mode, preserving historical behavior but leaving extension metadata unsupported for writes.
- `parallels_open()` may auto-repair writable, active images unless opened for check, inactive, or read-only.
- Allocation from backing currently reads full new clusters even when the subsequent write may overwrite most or all of them; comments call this out as inefficient.
