# File Research: sources/os/linux/linux/fs/jffs2/debug.c

This file implements JFFS2 sanity checks, paranoia checks, and debug dump helpers enabled through `debug.h` macros.

Sanity checks validate space accounting. `__jffs2_dbg_acct_sanity_check_nolock()` verifies that per-eraseblock sizes sum to `sector_size` and global superblock sizes sum to `flash_size`; failures log details and call `BUG()`. The locked wrapper takes `erase_completion_lock`.

Paranoia checks add structural validation. `__jffs2_dbg_fragtree_paranoia_check_nolock()` walks an inode fragment tree, checking that pristine nodes are not multiply fragmented and do not share partial pages with neighboring non-hole fragments. `__jffs2_dbg_prewrite_paranoia_check()` reads the target flash range and asserts it is all `0xff` before writing. `__jffs2_dbg_acct_paranoia_check_nolock()` recomputes eraseblock used/unchecked/dirty accounting from raw node refs and compares list-level superblock counts via `__jffs2_dbg_superblock_counts()`.

Dump helpers print raw node-ref chains, eraseblock accounting, all block lists, inode fragment trees, arbitrary buffers, and decoded node contents. `__jffs2_dbg_dump_node()` reads a node from flash, validates common header CRC and magic, then decodes inode and dirent node fields including node/name/data CRC information.

Key dependencies: `nodelist.h`, `debug.h`, MTD flash read helpers, CRC32, inode fragment and eraseblock structures.

Important invariant coverage: this file is the defensive layer for JFFS2’s manually maintained accounting and raw-node/fragment relationships. Many failures intentionally halt the kernel because corruption means allocator, GC, or mount state has become internally inconsistent.
