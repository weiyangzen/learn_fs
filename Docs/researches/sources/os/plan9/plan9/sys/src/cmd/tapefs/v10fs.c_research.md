# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/v10fs.c

This file implements a read-only tapefs backend for 10th Edition Unix 4 KB filesystem images.

Key behavior:
- Opens an image, records its length, reads the root inode, and initializes the tapefs root.
- Lazily reads directory entries and populates child nodes.
- Reads inode metadata and block address arrays.
- Maps direct and singly indirect block numbers to physical blocks.
- Prevents reads past the image length by returning zero-filled blocks.

Important details:
- Uses 4096-byte blocks and 14-character directory names.
- Character/block device files are exposed with zero size.
- Only singly-indirect files are supported.
- `doread` returns `buf+off`, correctly accounting for intra-block offsets.

Filesystem relevance:
- Direct: mounts a historical local filesystem image through the tapefs 9P interface.
