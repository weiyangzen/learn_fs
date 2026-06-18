# File Research: sources/os/linux/linux/fs/nilfs2/direct.c

This file implements NILFS2’s direct block-pointer bmap format, used for small mappings before conversion to B-tree form.

Data model:
- Direct pointers are stored inline after `struct nilfs_direct_node` in the bmap union.
- `NILFS_DIRECT_NBLOCKS` determines how many block offsets can be represented.
- Missing entries are encoded as `NILFS_BMAP_INVALID_PTR`.

Lookup:
- `nilfs_direct_lookup()` returns the pointer for a single key when level is `1`.
- `nilfs_direct_lookup_contig()` returns a contiguous physical run by scanning adjacent direct entries and translating virtual block numbers through DAT when needed.
- DAT `-ENOENT` during contiguous lookup is converted to `-EINVAL` to signal metadata corruption to the bmap layer.

Mutation:
- `nilfs_direct_insert()` rejects out-of-range keys and existing pointers, allocates a pointer through bmap/DAT helpers, marks the provided data buffer volatile, stores the allocated pointer, updates target hints, dirties the bmap, and increments block counts.
- `nilfs_direct_delete()` prepares and commits end-pointer handling, clears the direct pointer, and decrements block counts.
- `nilfs_direct_seek_key()` and `nilfs_direct_last_key()` scan inline pointers for the next/last valid key.
- `nilfs_direct_gather_data()` extracts valid direct pointers for conversion.

Conversion:
- `nilfs_direct_delete_and_convert()` deletes one entry using current ops, clears old resources if needed, rebuilds the inline pointer array from supplied key/pointer arrays, and reinitializes the bmap as direct.

Propagation and assignment:
- `nilfs_direct_propagate()` handles dirty data blocks in virtual pointer mode by updating DAT entries and marking buffers volatile.
- `nilfs_direct_assign()` validates key and pointer, then:
  - in virtual mode, starts the DAT entry with the assigned physical block and fills virtual block info
  - in physical mode, replaces the direct pointer with the physical block and fills DAT-style block info

Exported operations:
- `nilfs_direct_init()` installs the direct bmap operation table.
- Operation table includes lookup, contig lookup, insert/delete, propagate, assign, seek/last-key, insert check, and data gathering.
