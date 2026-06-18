# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_leaf.c

## Purpose

`xfs_attr_leaf.c` implements shortform attributes, attr leaf blocks, and the leaf-level operations used by attr btrees. It covers on-disk header conversion and verification, shortform create/add/remove/get/verify, shortform-to-leaf and leaf-to-shortform conversion, leaf-to-node conversion, leaf insertion/removal, split/rebalance/join support, lookup and getvalue, list support helpers, freemap compaction, and INCOMPLETE flag manipulation.

## Format Handling

The file supports two on-disk leaf header formats:

- legacy attr leaf blocks;
- CRC-enabled attr3 leaf blocks with owner, uuid, block number, checksum, and larger metadata header.

`xfs_attr3_leaf_hdr_from_disk` and `xfs_attr3_leaf_hdr_to_disk` translate between disk structures and `struct xfs_attr3_icleaf_hdr`. The in-core `firstused` is 32-bit because 64 KiB attr blocks can overflow the 16-bit disk field. The disk value zero is treated as a special 64 KiB empty-block marker.

## Verification

`xfs_attr3_leaf_verify` validates:

- da block header consistency;
- `firstused` bounds;
- entry array not colliding with name/value storage;
- nondecreasing hash order;
- name/value entry bounds;
- remote entries having a value block unless incomplete;
- freemap alignment, bounds, overflow, and non-overlap.

`xfs_attr3_leaf_read` reads attr fork buffers with leaf buffer ops, checks CRC-format owner when applicable, marks attr fork sickness on corruption, and sets the transaction buffer type.

## Shortform Operations

Shortform attrs are packed inside the inode attr fork:

- `xfs_attr_shortform_create` initializes a local attr fork and header.
- `xfs_attr_sf_findname` scans packed entries using namespace-aware matching.
- `xfs_attr_shortform_replace` updates same-sized values or parent-pointer name/value pairs in place.
- `xfs_attr_shortform_add` appends a packed entry, updates `i_forkoff`, logs inode core/attr data, and enables the attr2 superblock bit if needed.
- `xfs_attr_sf_removename` removes an entry, compacts the packed array, and may remove the attr fork entirely when empty and allowed.
- `xfs_attr_shortform_getvalue` delegates value copying to the shared helper.
- `xfs_attr_shortform_verify` checks packed entry bounds, nonzero names, namespace flags, and exact buffer consumption.

`xfs_attr_shortform_bytesfit` is the fork-layout gatekeeper. It balances inode literal-area space between data and attr forks and handles device inodes, extent forks, btree data forks, and minimum root-space requirements.

## Conversion Paths

- `xfs_attr_shortform_to_leaf` copies packed shortform data to a temporary buffer, converts the attr fork to extents, allocates block 0, creates an attr leaf, and reinserts all entries in hash order.
- `xfs_attr3_leaf_to_shortform` shrinks a leaf block back into the inode when all surviving entries are local and fit. It can also remove the attr fork entirely when the caller passed `forkoff == -1`.
- `xfs_attr3_leaf_to_node` copies the single leaf to a new block and creates a root da node at block 0 with one btree pointer to the copied leaf.

These conversions are transaction-logged and rely on bmap/da helpers to grow or shrink the attr fork.

## Leaf Add, Remove, Split, and Rebalance

`xfs_attr3_leaf_add` tries to insert a new entry into a leaf. It searches the three-entry freemap, compacts holes if necessary, and calls `xfs_attr3_leaf_add_work` when space is available. Local values are copied inline. Remote values create only the name entry, set INCOMPLETE, set remote block counters in `args`, and defer allocation/writing to `xfs_attr_remote.c`.

`xfs_attr3_leaf_remove` removes the indexed entry, updates/coalesces freemap regions, zeroes removed name/value storage, compacts the entry array, recomputes `firstused` if needed, and returns whether the leaf is under the low-fill threshold.

`xfs_attr3_leaf_split` allocates a new leaf, rebalances entries between leaves, links sibling pointers, inserts the new entry in the selected leaf, and returns whether higher-level da split work is still required.

`xfs_attr3_leaf_rebalance` and `xfs_attr3_leaf_figure_balance` choose how many entries remain in the lower leaf by minimizing byte imbalance, while also updating attr replacement tracking fields (`index`, `blkno`, `index2`, `blkno2`).

`xfs_attr3_leaf_toosmall` and `xfs_attr3_leaf_unbalance` support btree shrink/join by deciding whether a leaf should be dropped or merged with a sibling and by moving entries into the retained leaf.

## Lookup and Value Copy

`xfs_attr3_leaf_lookup_int` binary-searches by hash, walks duplicate-hash entries, performs namespace/name/value matching, and sets `args->index` either to the found entry or insertion point. It returns `-EEXIST` for found and `-ENOATTR` for missing.

`xfs_attr3_leaf_getvalue` verifies the indexed entry matches the requested name and copies local values or prepares remote-value metadata before calling the shared copy helper. Parent-pointer lookups compare the value as part of identity and do not copy values back to the caller.

## Atomic Replace Support

The INCOMPLETE flag is central to crash-safe attr replacement:

- `xfs_attr3_leaf_setflag` marks an existing entry incomplete and clears remote metadata for remote entries.
- `xfs_attr3_leaf_clearflag` makes a new entry complete and fills in remote value block/length if needed.
- `xfs_attr3_leaf_flipflags` clears INCOMPLETE on the new entry and sets it on the old entry in a single transaction, even when the two entries live in different leaf blocks.

## Dependencies and Risks

This file depends on da btree, bmap, transaction logging, buffer verifiers, health marking, error tags, remote attr helpers, and parent-pointer matching. Subtle areas include freemap overlap/zero-length handling, 64 KiB `firstused` conversion, duplicate-hash lookup, old/new index tracking during split, and the rule that remote-value buffers must be fully written before clearing INCOMPLETE.
