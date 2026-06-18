# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/32vfs.c

This file implements a read-only tapefs backend for VAX 32V/pre-FFS Berkeley filesystem images.

Key behavior:
- Opens a disk image, reads the root inode, and makes it the tapefs root.
- Lazily populates directories by reading fixed 14-character directory entries.
- Reads inodes from the inode area after the superblock.
- Maps logical file blocks through direct and singly indirect block addresses.
- Reads file data blocks into a static buffer.

Important details:
- Default block size is 512 bytes; `-b 1024` supports 4.1BSD-style images.
- Device special files report zero size.
- Only singly-indirect files are supported.
- Filesystem writes/truncates/creates are disabled.

Filesystem relevance:
- Direct: interprets a historical Unix filesystem image and exports it through tapefs’s 9P server.
