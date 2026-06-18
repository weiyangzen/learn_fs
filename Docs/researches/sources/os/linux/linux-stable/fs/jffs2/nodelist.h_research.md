# File Research: sources/os/linux/linux-stable/fs/jffs2/nodelist.h

## Role

Primary private JFFS2 implementation header. It defines endian conversion helpers, raw-node reference structures, inode cache structures, fragment/dnode/dirent/eraseblock structures, allocation constants, helper macros, and cross-file function prototypes.

## Endian and Mode Helpers

- Selects native, big-endian, or little-endian JFFS2 conversion macros.
- Converts 16-bit, 32-bit, and mode fields between CPU and JFFS2 raw wrapper types.
- Includes OS-specific glue through `os-linux.h` or `os-ecos.h`.

## Raw Node References

- `struct jffs2_raw_node_ref` stores physical flash offset plus low-bit status flags and the next-in-inode chain pointer.
- Low two bits of `flash_offset` encode:
  - `REF_UNCHECKED`;
  - `REF_OBSOLETE`;
  - `REF_PRISTINE`;
  - `REF_NORMAL`.
- `REF_LINK_NODE` and `REF_EMPTY_NODE` implement linked raw-ref blocks.
- `ref_next()`, `ref_flags()`, `ref_offset()`, `ref_obsolete()`, and `mark_ref_normal()` are central raw-ref helpers.
- `dirent_node_state()` treats live dirents as pristine and deletion dirents as normal.

## Inode and Node Structures

- `struct jffs2_inode_cache` is the always-resident per-inode summary:
  - scan-time dirents;
  - raw node list;
  - class/state/flags;
  - inode number;
  - xattr association;
  - parent inode or link count.
- Inode states include unchecked, checking, present, checked absent, GC, reading, and clearing.
- `struct jffs2_full_dnode` represents instantiated data/metadata nodes.
- `struct jffs2_tmp_dnode_info` supports read-inode reconstruction.
- `struct jffs2_readinode_info` groups read-inode temporary state.
- `struct jffs2_full_dirent` is an in-memory directory entry with variable-length name.
- `struct jffs2_node_frag` maps a logical file range to a full dnode or hole.
- `struct jffs2_eraseblock` tracks per-block list linkage, accounting, raw refs, and GC cursor.

## Constants and Inline Helpers

- `JFFS2_MIN_NODE_HEADER` uses raw dirent size.
- `REFS_PER_BLOCK` targets raw ref blocks around 256 bytes.
- `write_ofs(c)` computes the next physical write offset in `nextblock`.
- Allocation priorities: normal, deletion, GC, no-retry.
- `VERYDIRTY()`, `ISDIRTY()`, and `PAD()` provide common accounting/alignment checks.
- `jffs2_encode_dev()` chooses old or new device encoding.
- Fragment and tmp-node red-black tree traversal macros wrap Linux rb helpers.

## Cross-File API Surface

Declares APIs from:

- `nodelist.c`: dirent lists, inode cache management, fragment trees, raw refs.
- `nodemgmt.c`: reservation, physical refs, completion, obsolete marking.
- `write.c`: new inode, dnode/dirent writes, range writes, create/unlink/link.
- `readinode.c`: inode read, CRC check, inode clear.
- `malloc.c`: object allocators.
- `gc.c`: garbage collection pass.
- `read.c`: dnode/range/link reads.
- `scan.c`: flash scan and block classification.
- `build.c`: mount build.
- `erase.c`: erase pending blocks and ref freeing.
- `wbuf.c`: writebuffer operations when configured.

## Research Notes

This header is the internal contract for nearly all JFFS2 files. The most important design point is that raw node refs are tiny physical records, while full dnodes/fragments are built only for in-core inodes; this keeps mount-wide memory lower than storing every logical mapping eagerly.
