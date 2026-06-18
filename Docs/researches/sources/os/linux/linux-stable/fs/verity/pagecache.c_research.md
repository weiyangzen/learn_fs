# File Research: sources/os/linux/linux-stable/fs/verity/pagecache.c

Provides generic helpers for filesystems that store Merkle tree blocks in the inode pagecache. `generic_read_merkle_tree_page()` reads a page/folio at a filesystem-adjusted page index and returns the page corresponding to that index. `generic_readahead_merkle_tree()` starts readahead for Merkle tree pages if the target page is absent or not uptodate.

Both helpers require the filesystem to translate fs-verity’s Merkle-tree-relative index to the actual pagecache index where metadata is stored. Readahead asserts the mapping invalidate lock is held, matching the locking expectations used by fs-verity metadata reads.
