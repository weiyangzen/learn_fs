# File Research: sources/os/linux/linux-stable/fs/jffs2/nodelist.c

## Role

Implements core in-memory JFFS2 node-list operations: directory entry list replacement, fragment tree updates/truncation, inode cache hash management, raw node ref linking/freeing, dirty-space scanning, and raw ref length calculation.

## Directory Entries

- `jffs2_add_fd_to_list()` keeps the directory entry list sorted by name hash.
- Replaces older entries with newer same-name versions.
- Marks replaced raw nodes obsolete when possible and frees the old full dirent.

## Fragment Tree

- `jffs2_truncate_fragtree()` removes or shrinks fragments beyond a new size and marks affected nodes obsolete/normal.
- `jffs2_obsolete_node_frag()` decrements backing dnode fragment counts and marks nodes obsolete when their final fragment disappears.
- `jffs2_add_frag_to_fragtree()` inserts a new data fragment into the red-black tree, splitting or obsoleting overlapping fragments and inserting hole fragments when needed.
- `jffs2_add_full_dnode_to_inode()` wraps a full dnode in a fragment, inserts it, and marks page-sharing nodes `REF_NORMAL` for safer GC.
- `jffs2_lookup_node_frag()` finds the fragment covering an offset or the closest preceding fragment.
- `jffs2_kill_fragtree()` frees all fragments and optionally marks backing nodes obsolete.

## Inode Cache Management

- `jffs2_set_inocache_state()` updates inode-cache state and wakes waiters.
- `jffs2_get_ino_cache()` looks up an inode cache in the sorted hash bucket.
- `jffs2_add_ino_cache()` assigns an inode number if needed and inserts into the sorted hash chain.
- `jffs2_del_ino_cache()` removes a cache and frees it unless it is in reading/clearing transition.
- `jffs2_free_ino_caches()` frees all inode caches and xattr associations.

## Raw Node Refs

- `jffs2_free_raw_node_refs()` frees all refblocks for all eraseblocks.
- `jffs2_link_node_ref()` consumes a preallocated ref, attaches it to an eraseblock and optional inode cache, validates physical contiguity, and updates used/unchecked/dirty/free accounting based on ref flags.
- `jffs2_scan_dirty_space()` accounts dirty space during mount scan and merges with the previous obsolete ref when possible.
- `__jffs2_ref_totlen()` calculates a raw ref’s total length from the next ref or eraseblock free boundary, with optional `TEST_TOTLEN` validation.

## Research Notes

This file enforces the logical map of current file contents. Overlapping log nodes are resolved by fragment-tree surgery, and obsolete/live status is mirrored into raw node ref flags so GC can later decide whether to copy, rewrite, or discard physical nodes.
