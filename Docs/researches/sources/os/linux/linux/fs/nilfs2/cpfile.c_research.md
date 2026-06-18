# File Research: sources/os/linux/linux/fs/nilfs2/cpfile.c

This file implements the NILFS2 checkpoint metadata file. It manages checkpoint records, checkpoint statistics, deletion of old checkpoints, snapshot conversion, snapshot list traversal, and cpfile inode initialization.

Indexing and layout:
- Checkpoint number `0` is invalid; valid checkpoints begin at `1`.
- Helpers map checkpoint numbers to metadata-file block offsets and entry offsets using `mi_entries_per_block` and `mi_first_entry_offset`.
- The first cpfile block contains `struct nilfs_cpfile_header`; checkpoint entries are `struct nilfs_checkpoint`.
- Blocks maintain a valid-checkpoint count used to delete empty checkpoint blocks outside the first block.

Checkpoint lifecycle:
- `nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, clears the invalid bit, increments block/header counts, and dirties cpfile metadata.
- `nilfs_cpfile_finalize_checkpoint()` fills final counts, block increment, creation time, minor flag, checkpoint number, and the ifile inode snapshot.
- `nilfs_cpfile_read_checkpoint()` reads checkpoint metadata into a `nilfs_root` and associated ifile inode, treating invalid checkpoint entries or corrupted ifile data as errors.
- `nilfs_cpfile_delete_checkpoints()` invalidates non-snapshot checkpoints over a range, skips holes, refuses snapshots with `-EBUSY`, decrements statistics, and deletes now-empty checkpoint blocks.
- `nilfs_cpfile_delete_checkpoint()` validates one checkpoint through cpinfo lookup before deleting it.

Snapshot handling:
- Snapshots are maintained in a doubly-linked list anchored in the cpfile header.
- `nilfs_cpfile_set_snapshot()` inserts a checkpoint into the sorted snapshot list and increments `ch_nsnapshots`.
- `nilfs_cpfile_clear_snapshot()` removes it from that list, clears snapshot links/flag, and decrements `ch_nsnapshots`.
- `nilfs_cpfile_change_cpmode()` switches between checkpoint and snapshot modes; mounted snapshots cannot be converted back to plain checkpoints.

Information queries:
- `nilfs_cpfile_get_cpinfo()` dispatches to normal checkpoint scan or snapshot-list scan.
- Normal scan finds existing checkpoint blocks over the cpfile bmap and skips invalid entries.
- Snapshot scan follows `ssl_next` links from the header or caller-provided continuation point.
- `nilfs_cpfile_get_stat()` reads total checkpoint and snapshot counts from the header.

Concurrency:
- Uses `NILFS_MDT(cpfile)->mi_sem`:
  - read lock for queries and reads
  - write lock for create/finalize/delete/mode changes
- Snapshot mode changes are additionally serialized at ioctl level by the snapshot mount mutex.

Error handling:
- Missing header block is logged as metadata corruption and returned as `-EIO`.
- Hole checkpoint blocks may be benign during scans/deletion but are errors in paths requiring an existing checkpoint.
- Invalid ranges return `-EINVAL`; snapshots being deleted return `-EBUSY`.

Initialization:
- `nilfs_cpfile_read()` validates checkpoint entry size, creates/gets `NILFS_CPFILE_INO`, initializes metadata-file state, sets entry geometry, and imports the raw inode.
