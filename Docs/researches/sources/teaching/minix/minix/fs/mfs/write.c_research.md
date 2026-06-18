# File Research: sources/teaching/minix/minix/fs/mfs/write.c

`write.c` is the write-side counterpart to `read.c`, responsible for updating inode block maps, allocating blocks, freeing zones, and zeroing buffers.

`write_map` maps a file byte position to the correct direct, single-indirect, or double-indirect slot and either writes a new zone number or frees the existing zone when `WMAP_FREE` is set. It allocates missing indirect and double-indirect blocks as needed, zeroes newly allocated indirect blocks, writes entries with `wr_indir`, and frees now-empty indirect blocks using `empty_indir`. It marks the inode dirty before map updates and maintains references in either the inode zone array or indirect blocks.

`wr_indir` writes one zone entry to an indirect block using `conv4`. `empty_indir` scans an indirect block for any non-`NO_ZONE` entry. `clear_zone` is now effectively a no-op because the implementation asserts block size equals zone size (`s_log_zone_size == 0`).

`new_block` allocates a zone if `read_map` finds no existing block at the requested position, using `i_zsearch` and the first file zone as locality hints, records the mapping with `write_map`, obtains a VM-cache-aware buffer with `lmfs_get_block_ino(..., NO_READ, ...)`, zeroes it, and returns it. `zero_block` clears a buffer's data to zero and marks it dirty.
