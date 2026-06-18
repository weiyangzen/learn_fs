# File Research: sources/local-fs/mtd-utils/mkfs.jffs2.c

## Purpose
Implements the `mkfs.jffs2` utility, building a JFFS2 image from a host directory tree with optional device-table entries, compression settings, xattrs, endian selection, cleanmarkers, padding, ownership/permission squashing, fake timestamps, and incremental image parsing.

## Main Data Model
`struct filesystem_entry` represents the target filesystem tree. It stores target and host paths, stat metadata, symlink target, parent/child/sibling links, JFFS2 inode number, and a red-black node for hardlink tracking.

## Build Flow
`main()` parses options, initializes compressors, chooses page and eraseblock sizes, opens output and optional incremental input, `chdir()`s into the root, optionally parses an existing image to continue inode numbering, recursively scans the host tree, applies a device table, and calls `create_target_filesystem()`.

Host scanning is handled by `recursive_add_host_directory()` and `add_host_filesystem_entry()`. Device table parsing can create or override files, directories, FIFOs, and character/block devices. `find_hardlink()` records host `(st_dev, st_ino)` pairs to emit later hardlinks as additional dirents to an existing JFFS2 inode.

## Image Serialization
The writer emits raw JFFS2 dirent and inode nodes with CRCs and target-endian conversions. Regular files are split by page and eraseblock space, compressed through the JFFS2 compressor framework, and padded to word alignment. Directories, FIFOs, sockets, symlinks, and special files have specialized writers. `pad_block_if_less_than()` handles cleanmarker insertion and eraseblock boundary padding.

When xattr support is enabled, xattrs are read from the host with `llistxattr()`/`lgetxattr()`, ACLs are converted to JFFS2 ACL format, duplicate xattr bodies are interned, and xref nodes connect inodes to xattr IDs.

## Dependencies
Uses JFFS2 UAPI structures, `crc32`, the local compressor framework, local red-black tree helpers, POSIX filesystem APIs, and optional xattr/ACL headers.

## Risks and Notes
This is a stateful single-process image builder with global output offset, inode counter, compression state, and endian mode. Incremental parsing only scans node headers to advance inode numbering; it does not validate or rewrite the old image. The `cleanup()` routine clears `e->next` before advancing, so it can stop after the first child and leak the rest of a directory tree.
