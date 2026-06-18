# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_reblock.c

Purpose: implements HAMMER reblocking, which relocates records, data, and/or B-tree nodes out of fragmented big-blocks so the old big-blocks can become fully free.

Top-level behavior: `hammer_ioc_reblock()` validates object-id range and free threshold, maps a high `free_level` to emergency space checking, derives localizations for current PFS or all PFSs, and scans the B-tree. It optionally asks the scan to return internal nodes when `HAMMER_IOC_DO_BTREE` is set.

Decision logic: `hammer_reblock_helper()` first handles record data only for leaf record elements with nonzero `data_offset`. Record type maps to ioctl class flags: inodes/snapshots/config, directories/metadata records, or file data/database records. It then checks target volume filtering, accounts candidate bytes, queries free bytes in the current big-block, and relocates only when the big-block meets the threshold and is not the allocator's current big-block unless forced by threshold zero.

Data relocation: `hammer_reblock_data()` extracts existing data, allocates a new data block, copies the payload, recalculates the leaf CRC using the current filesystem version, invalidates cursor data cache before freeing the old block, updates `data_offset` and `data_crc` in the B-tree node, and releases the new buffer.

B-tree node relocation: `hammer_reblock_leaf_node()` and `hammer_reblock_int_node()` allocate a new node, copy the old node through `hammer_move_node()`, update parent/root references, update children parent pointers for internal nodes, inform cursor tracking, delete the old node, and replace the cursor node.

Operational behavior: the code carefully unlocks around vnode-cache uncaching and buffer-cache pressure, then retests cursor stability. It retries on `EWOULDBLOCK` after a sync and on `EDEADLK`, handles interrupts with ioctl flags, and pauses for metadata/UNDO pressure. Reblocking is sync-lock protected during individual relocation work.
