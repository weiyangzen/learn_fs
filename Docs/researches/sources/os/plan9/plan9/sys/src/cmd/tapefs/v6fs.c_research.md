# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/v6fs.c

This file implements a read-only tapefs backend for old V6-and-earlier PDP-11 Unix filesystem images.

Key behavior:
- Opens an image and reads root inode 1.
- Lazily populates directories from 14-character V6 directory entries.
- Parses V6 inode flags, size, owner/group, timestamps, and eight block addresses.
- Maps small files through direct addresses and larger files through single-indirect blocks.
- Reads file data from 512-byte blocks.

Important details:
- V6 directory mode is recognized through the V6-specific format bits.
- Large-file handling assumes file size predicts indirect addressing.
- Device special files are treated as zero-length.
- Write/create/truncate operations are disabled.

Filesystem relevance:
- Direct: exposes old Unix filesystem images as a Plan 9 mounted namespace.
