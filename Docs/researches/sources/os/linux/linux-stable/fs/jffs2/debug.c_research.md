# File Research: sources/os/linux/linux-stable/fs/jffs2/debug.c

## Role

Implements JFFS2 debug-time sanity checks, paranoia checks, and dump helpers for eraseblock accounting, inode fragment trees, raw node references, buffers, and on-flash node contents.

## Sanity Checks

- `__jffs2_dbg_acct_sanity_check_nolock()` verifies:
  - per-eraseblock accounting sums to `sector_size`;
  - superblock space accounting sums to `flash_size`.
- `__jffs2_dbg_acct_sanity_check()` wraps the nolock check with `erase_completion_lock`.

## Paranoia Checks

- `__jffs2_dbg_fragtree_paranoia_check*()` validates invariants around `REF_PRISTINE` nodes:
  - pristine nodes should not have multiple frags;
  - adjacent same-page non-hole frags require normal GC handling.
- `__jffs2_dbg_prewrite_paranoia_check()` reads flash before a write and BUGs if the target area is not erased.
- `__jffs2_dbg_superblock_counts()` recounts every block list and verifies aggregate counters and block count membership.
- `__jffs2_dbg_acct_paranoia_check*()` walks raw node refs in an eraseblock, recalculates used/unchecked/dirty sizes, validates last-node linkage, and optionally triggers full superblock recounting.

## Dump Helpers

- `__jffs2_dbg_dump_node_refs*()` prints raw node refs for an eraseblock.
- `__jffs2_dbg_dump_jeb*()` prints eraseblock accounting.
- `__jffs2_dbg_dump_block_lists*()` prints all major eraseblock lists and accounting totals.
- `__jffs2_dbg_dump_fragtree*()` prints the logical fragment tree for an inode and BUGs on holes in expected continuity.
- `__jffs2_dbg_dump_buffer()` hex-dumps a buffer at a flash offset.
- `__jffs2_dbg_dump_node()` reads and prints an on-flash inode or dirent node, validating common/header CRCs.

## Dependencies

Uses JFFS2 node list structures, MTD flash reads, CRC32, page sizing, and debug macros from `debug.h`.

## Research Notes

This file is compiled conditionally by debug feature macros. The lightweight accounting sanity path is always exposed through `JFFS2_DBG_SANITY_CHECKS`, while heavier paranoia and dump code only exists when debug options enable it.
