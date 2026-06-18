# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose
Implements XFS shortform and leaf-block attribute formats, including on-disk verifiers, shortform packing, shortform-to-leaf and leaf-to-shortform conversion, leaf insertion/removal, leaf split/rebalance/join operations, lookup/value retrieval, and `XFS_ATTR_INCOMPLETE` flag manipulation.

## Main Interfaces
- Buffer format verification/read: `xfs_attr3_leaf_read()`, `xfs_attr3_leaf_header_check()`, `xfs_attr3_leaf_hdr_from_disk()`, `xfs_attr3_leaf_hdr_to_disk()`, `xfs_attr3_leaf_buf_ops`.
- Shortform operations: `xfs_attr_shortform_create()`, `xfs_attr_sf_findname()`, `xfs_attr_shortform_replace()`, `xfs_attr_shortform_add()`, `xfs_attr_sf_removename()`, `xfs_attr_shortform_getvalue()`, `xfs_attr_shortform_to_leaf()`, `xfs_attr_shortform_allfit()`, `xfs_attr_shortform_verify()`.
- Leaf/tree operations: `xfs_attr3_leaf_create()`, `xfs_attr3_leaf_init()`, `xfs_attr3_leaf_split()`, `xfs_attr3_leaf_add()`, `xfs_attr3_leaf_remove()`, `xfs_attr3_leaf_to_node()`, `xfs_attr3_leaf_to_shortform()`, `xfs_attr3_leaf_toosmall()`, `xfs_attr3_leaf_unbalance()`.
- Lookup/value/utility: `xfs_attr3_leaf_lookup_int()`, `xfs_attr3_leaf_getvalue()`, `xfs_attr_leaf_lasthash()`, `xfs_attr_leaf_order()`, `xfs_attr_leaf_newentsize()`.
- Crash-consistency flags: `xfs_attr3_leaf_clearflag()`, `xfs_attr3_leaf_setflag()`, `xfs_attr3_leaf_flipflags()`.

## On-Disk Verification
The verifier checks attr leaf magic, CRC metadata, owner, sorted hash order, entry array bounds, name/value region bounds, nonzero name lengths, remote value block presence for complete remote entries, `firstused` validity, freemap alignment, freemap bounds, integer overflow, and freemap overlap. Attr3 64 KiB block handling maps a disk `firstused` value of zero to the full block size for empty blocks because the on-disk field is only 16 bits.

## Shortform Flow
Shortform attributes live in the inode literal area. Creation initializes an `xfs_attr_sf_hdr`, additions append compact name/value entries and adjust `i_forkoff`, replacements update in place only when the stored size remains compatible, and removals memmove later entries over the deleted one. If the final entry disappears and no parent-pointer feature constraints require keeping the fork, the attr fork is removed. Shortform verification checks total size, entry bounds, nonzero names, valid flags, and namespace combinations.

## Leaf And Btree Flow
Leaf add first searches freemap entries for a first-fit region; if fragmented, it compacts the block and retries. Local values store name and value directly in the leaf; large values create a remote entry, mark it incomplete, and return remote block requirements to the higher-level state machine. Leaf removal updates freemaps, clears name/value storage, compacts the entry array, recomputes `firstused` when needed, and reports whether the block is below the join threshold.

Single leaf blocks convert to node format by allocating a new block, copying the old leaf there, and creating a root node pointing to the copied leaf. Splits allocate a new leaf, rebalance entries by byte usage, link sibling blocks, and track old/new entry locations for replacement operations. Shrink paths test if leaves can be joined with siblings, move entries into the retained leaf, and update last hash values for DA Btree fixup.

## Lookup And Values
`xfs_attr3_leaf_lookup_int()` binary-searches by hash, scans duplicate hash entries, and compares namespace, incomplete bit handling, name, and parent-pointer value when relevant. Local values are copied directly. Remote entries populate `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` before `xfs_attr_copy_value()` calls remote IO.

## Integration Points
Works with `xfs_attr.c` for high-level operation sequencing, `xfs_attr_remote.c` for remote values, `xfs_da_btree` for splits/joins/path shifts, inode literal-area helpers, bmap local-to-extents conversion, superblock attr2 feature logging, transaction buffer logging, CRC buffer ops, health marking, and parent-pointer matching semantics.

## Notable Behaviors
- Normal lookup includes the incomplete bit in the match mask; recovery lookup ignores it so recovery can find entries needing cleanup.
- Parent-pointer matching requires both name and value equality and does not support remote values.
- Leaf-to-shortform conversion skips incomplete entries and only accepts local entries.
- Leaf compaction preserves disk header fields outside the incore header before repacking entries.
- Remote entry creation zeros `valueblk` and `valuelen` until the remote value is written and the incomplete flag is cleared.

## Risks And Review Focus
- Freemap updates are delicate: insertion and removal both adjust entry-array boundaries and must avoid overlapping or stale zero-length freemap entries.
- Split/rebalance code must maintain `args->index`, `blkno`, `index2`, and `blkno2` correctly for atomic replace.
- Verifier changes must preserve 64 KiB attr block first-used conversion behavior.
- Incomplete-entry semantics differ between normal operation and recovery; lookup mask changes can expose partial attributes or hide recoverable ones.
