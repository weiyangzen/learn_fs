# File Research: sources/teaching/minix/minix/fs/isofs/utility.c

This ISOFS utility file contains small helpers for memory ownership, ISO directory extents, block retrieval, ISO 9660 timestamp conversion, and checked allocation. It includes `inc.h`, so it depends on ISOFS-wide state such as `fs_dev` and `v_pri`.

`free_extent` recursively frees a linked list of `struct dir_extent` nodes. `free_inode_dir_entry` frees the dynamic record name (`r_name`) inside an `inode_dir_entry` but deliberately leaves the entry object itself allocated for the caller to manage.

`get_extent_absolute_block_id` maps a byte/block offset within an extent chain to an absolute ISO logical block number. It divides the supplied offset by the volume logical block size, walks the linked extents by length, and returns zero if the target falls outside the chain. `read_extent_block` builds on that mapper, rejects block zero and blocks beyond `volume_space_size_l`, and then retrieves the block with `lmfs_get_block`.

`date7_to_time_t` converts ISO 9660's 7-byte date format into a `time_t` using `struct tm`, applying the quarter-hour timezone byte as an hour adjustment when the value is in the legal range. `alloc_mem` wraps `calloc(1, size)` and asserts success, giving ISOFS zero-filled allocations with fail-fast semantics.
