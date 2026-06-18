# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/chk.c

cwfs filesystem checker and optional repair logic.

`cmd_check` parses check options, locks the filesystem when writable, reads the superblock/root, allocates block/qid bitmaps, recursively walks the directory tree, validates tags and qids, detects duplicate/out-of-range blocks, optionally reads all file data, prints files/directories, rebuilds tags, clears bad references, touches old blocks, trims filesystem size, and rebuilds or checks the free list. It reports used/free/missing/bad/qid counts and recursion stack usage.

The checker traverses direct and multi-level indirect blocks using `fsck`, `dirck`, `indirck`, and address validators. Free-list handling differs for normal and copy-on-write/read-only devices: `mkfreelist` rebuilds from scratch for writable normal devices, while `trfreelist` filters an existing list for cw devices.
