# File Research: sources/os/linux/linux-stable/fs/afs/dir_edit.c

This file performs local edits to cached AFS directory blobs after server-confirmed mutations.

Major responsibilities:
- Finds, sets, and clears contiguous slot bits in an AFS directory block bitmap.
- Maps directory blocks from a vnode’s folio-queue directory buffer, extending the buffer if needed.
- Scans directory blocks for names.
- Initializes new directory blocks and block-zero metadata.
- Adds, removes, or updates directory entries in cached directory data.
- Initializes the `.` and `..` entries for a newly created directory.

Directory block model:
- Each AFS directory block has 64 slots; slot zero is metadata.
- Block zero has additional reserved slots and allocation counters/hash table metadata.
- Entry length determines slot count with `afs_dir_calc_slots()`.
- The first `AFS_DIR_BLOCKS_WITH_CTR` blocks have allocation counters stored in block-zero metadata.
- Hash buckets in block zero point to slot entries; dirents have `hash_next` links.

Add edits:
- `afs_edit_dir_add()` validates directory size, maps metadata block, calculates required slots, searches existing or newly initialized blocks for contiguous free slots, writes the dirent, sets bitmap bits, decrements allocation counters, inserts into the hash chain, increments inode version, and marks the directory dirty.
- If the directory cache is invalid, too large, oddly sized, out of slots despite server success, or otherwise inconsistent, it invalidates the directory instead of forcing an unsafe edit.

Remove edits:
- `afs_edit_dir_remove()` validates size, initializes a search iterator, finds the target in its hash bucket, clears bitmap bits, increments allocation counters, zeroes dirent slots, and repairs the hash chain head or previous dirent link.
- Hash-chain mismatches emit warnings and abandon the edit path.
- On success, inode version is set to the server data version and the directory is marked dirty.

Update edits:
- `afs_edit_dir_update()` scans blocks for a named entry and updates its vnode/unique fields.
- It is used for replacing a dirent target and updating `..` during cross-directory renames.
- Missing entries or invalidated directories cause cache invalidation or edit abandonment.

New directory initialization:
- `afs_mkdir_init_dir()` requires a one-block directory, initializes block zero, writes `.` pointing to the new vnode and `..` pointing to the parent, sets two bitmap slots, updates allocation counters, marks the inode dirty, and sets directory valid/read flags.
