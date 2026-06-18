# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump.c

## Role

`dump.c` contains the formatting layer for `debugfs.ocfs2`. It turns OCFS2 and JBD2 on-disk structures into human-readable diagnostic text.

## Structures Dumped

It prints superblocks, inodes, local allocators, truncate logs, extent lists and blocks, chain lists, group descriptors, group free extents, directory entries and directory block trailers, directory-index roots/leaves/entry lists/free-space records, heartbeat blocks, slot maps, xattrs, refcount blocks/records, fragmentation summaries, and block checksums/ECC.

## Journal Support

It formats JBD2 headers, superblocks, descriptor blocks, commit blocks, revoke blocks, OCFS2 metadata blocks found inside journals, and unknown journal ranges that are probably file data.

## Checksum Handling

`dump_block_check()` prints stored CRC/ECC and validates known metadata blocks by swapping to disk format, recomputing metadata ECC, swapping back, and preserving the original block check contents.

## Dependencies

It relies on libocfs2 byte-order helpers, feature flag string helpers from `utils.c`, GLib strings, and `gbls.fs` for block size, checksum validation, and directory trailer interpretation.

## Risk Areas

This file mostly formats data, but some routines temporarily mutate buffers for byte swapping or directory-entry name termination. Callers must provide buffers that can be safely modified and restored.
