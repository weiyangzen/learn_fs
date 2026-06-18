# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/v10fs.c

`v10fs.c` is a `tapefs` backend for 10th Edition Unix 4K filesystems.

Format:
- Uses 4096-byte blocks.
- Disk inode resembles 32V with 13 three-byte addresses and 14-byte directory names.
- Root inode is 2; superblock offset constant is 1.
- Captures image length with `dirfstat` to guard against reads past EOF.

Behavior:
- `populate` opens the image, records length, reads root inode, and seeds root `Ram`.
- `popdir` lazily reads directory entries, skips `.`/`..` and inode 0, converts child inodes through `iget`, and inserts with `popfile`.
- `doread` maps offset to logical blocks and fills a static buffer.
- `iget` reads inode block and converts flags, size, addresses, uid/gid, and mtime.
- `getblk` maps logical block to disk block and zero-fills holes or out-of-image reads.
- `bmap` handles direct and singly indirect blocks.

Risks:
- Only singly indirect mapping is implemented.
- Static read buffer is not reentrant.
- Bad inode reads are fatal.
