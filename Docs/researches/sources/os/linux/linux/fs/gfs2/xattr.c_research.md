# File Research: sources/os/linux/linux/fs/gfs2/xattr.c

## Scope

This file implements GFS2 extended attribute storage, lookup, list, get, set, replace, remove, and full xattr fork deallocation. It supports stuffed xattr values stored in EA blocks and unstuffed values stored in separate EA data blocks, with optional indirect EA block lists.

## Public And Internal APIs Covered

- VFS/ACL-facing APIs: `gfs2_listxattr()`, `gfs2_xattr_acl_get()`, `__gfs2_xattr_set()`, xattr handler arrays `gfs2_xattr_handlers_max` and `gfs2_xattr_handlers_min`.
- Lookup/iteration: `ea_foreach()`, `ea_foreach_i()`, `gfs2_ea_find()`, `ea_find_i()`.
- Data access: `gfs2_iter_unstuffed()`, `gfs2_ea_get_copy()`, `__gfs2_xattr_get()`, `gfs2_xattr_get()`.
- Allocation/write: `ea_alloc_blk()`, `ea_write()`, `ea_alloc_skeleton()`, `ea_init()`, `ea_set_i()`, `ea_set_simple()`, `ea_set_block()`.
- Removal/deallocation: `gfs2_xattr_remove()`, `ea_remove_stuffed()`, `ea_remove_unstuffed()`, `ea_dealloc_unstuffed()`, `ea_dealloc_indirect()`, `ea_dealloc_block()`, `gfs2_ea_dealloc()`.

## Control Flow And Behavior

Size handling starts with `ea_calc_size()` and `ea_check_size()`. Stuffed values store name and data in one EA record; unstuffed values store name plus an array of block pointers, with value bytes in `GFS2_METATYPE_ED` blocks. Type validity is format-gated: max format accepts all known types, min format only permits user/system/security.

`ea_foreach()` reads `ip->i_eattr`. If the inode does not use `GFS2_DIF_EA_INDIRECT`, it iterates a single EA block. Otherwise it validates the indirect block and walks its block pointer array, reading each EA block. `ea_foreach_i()` validates each EA block's metadata type, nonzero record length, record bounds, type validity, and final record alignment to the block end.

Lookup uses `gfs2_ea_find()` to scan for a matching type/name pair and returns a held buffer plus EA and previous-record pointers in `struct gfs2_ea_location`. `gfs2_listxattr()` locks the inode glock shared, formats recognized namespace prefixes, and either counts or copies NUL-terminated names.

Get operations lock the inode glock shared unless already held. `__gfs2_xattr_get()` checks `i_eattr`, name length, and existence. Stuffed data is copied directly; unstuffed data is copied by reading every pointed data block, validating `GFS2_METATYPE_ED`, and copying up to `sd_jbsize` payload bytes per block.

Set operations lock quota accounting and the inode glock exclusively unless already held. `__gfs2_xattr_set()` rejects immutable/append inodes, overlong names, and oversized values. A `NULL` value means remove; a zero-length non-NULL value is a real xattr value. New xattr forks are initialized by allocating an EA block, setting `ip->i_eattr`, and writing the request.

Existing forks are updated by searching for space in current EA records. `ea_set_simple()` can reuse an unused record, split slack from an existing record, remove old stuffed state, or, if the new value is unstuffed, reserve blocks/quota and allocate data blocks through `ea_alloc_skeleton()`. If no current EA block has space, `ea_set_block()` either appends a new EA block to an existing indirect block or converts a direct EA fork into an indirect block that points to the old and new EA blocks.

`ea_write()` writes header fields, name, and either stuffed data or newly allocated unstuffed data blocks. For each unstuffed block it allocates a filesystem block, removes matching revokes, creates metadata, stamps `GFS2_METATYPE_ED`, copies payload after the meta header, zero-fills tail bytes, records the block pointer, and increments inode block count.

Removal coalesces stuffed records with their predecessor when possible or marks the first record unused. Unstuffed removal frees data blocks in contiguous runs from the same rgrp, zeros data pointers, decrements inode block count, optionally coalesces the EA record, and updates ctime/dirty state. Full fork deallocation first removes all unstuffed data, then frees indirect EA blocks if present, then frees the root EA/indirect block and clears `ip->i_eattr`.

## State And Data Structures

Important structures are `gfs2_ea_header`, `gfs2_ea_request`, `gfs2_ea_location`, indirect EA pointer blocks, unstuffed EA data blocks, inode fields `i_eattr` and `i_diskflags`, inode block counts, quota reservations, and rgrp lists for multi-rgrp frees.

## Dependencies

The file depends on GFS2 glocks, meta I/O, rgrp allocation/freeing, transactions, quota lock/hold/check logic, dinode serialization, ACL code, VFS xattr handlers, and POSIX ACL/security/user/trusted namespace conventions.

## Risks And Invariants

EA record walking must reject zero-length, out-of-bounds, bad-type, and misaligned final records to avoid corrupt metadata traversal. Replacing unstuffed xattrs requires careful two-phase behavior: write the new value, then remove old unstuffed blocks. Direct-to-indirect conversion must preserve the old EA block pointer. Block and quota reservations must cover EA blocks, data blocks, rgrp metadata, statfs, and quota changes. `GFS2_DIF_APPENDONLY` prevents replacing existing xattrs even if VFS append state checks passed.
