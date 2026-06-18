# File Research: sources/os/linux/linux/fs/jffs2/nodelist.h

This header defines JFFS2’s central in-core node, inode-cache, fragment, dirent, and eraseblock structures, plus conversion macros and subsystem prototypes.

It sets JFFS2 endian conversion helpers for native, big-endian, and little-endian builds, including mode conversion through OS-specific mode helpers. `JFFS2_MIN_NODE_HEADER`, `PAD()`, allocation priority constants, dirty thresholds, and `write_ofs(c)` are defined here.

`struct jffs2_raw_node_ref` is the compact per-raw-node in-core record. Its `flash_offset` lower two bits encode state: unchecked, obsolete, pristine, or normal. Helpers include `ref_next()`, `jffs2_raw_ref_to_ic()`, `ref_flags()`, `ref_offset()`, `ref_obsolete()`, and `mark_ref_normal()`. Refblocks use `REF_LINK_NODE` and `REF_EMPTY_NODE`.

`struct jffs2_inode_cache` tracks mount-wide inode metadata before or without a live VFS inode: raw node refs, inode state, inode number, hash linkage, xattr ref, and `pino_nlink` which stores parent inode for directories or link count for other inodes. The header defines inode states from unchecked through reading/clearing and raw-node classes for inode/xattr objects.

`struct jffs2_full_dnode`, `jffs2_tmp_dnode_info`, `jffs2_readinode_info`, `jffs2_full_dirent`, `jffs2_node_frag`, and `jffs2_eraseblock` define the higher-level in-core representations used by readinode, directories, file data maps, and eraseblock management.

The remainder declares cross-file APIs for nodelist, nodemgmt, write, readinode, malloc, GC, read, scan, build, erase, and writebuffer support, then includes `debug.h`.

Key dependencies: Linux VFS/types/rbtree, JFFS2 on-flash definitions, OS glue (`os-linux.h` or `os-ecos.h`), xattr/ACL/summary headers, and debug instrumentation.

Important design point: most on-flash node state is reconstructed from compact raw refs and inode caches; full dnodes/fragments are only built for active inodes.
