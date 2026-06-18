# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/mkfs.ubifs.c

## Purpose
Main `mkfs.ubifs` implementation. It builds a UBIFS image from a host directory tree or directly formats an UBI volume.

## Key Elements
Parses filesystem geometry, compression, reserved-space, device-table, owner-squash, and UBI/file output options. Initializes a reduced `ubifs_info`, writes data/dent/inode nodes, tracks LEB properties, builds the UBIFS index tree, reserves a GC LEB, finalizes LEB counts, then writes LPT, superblock, master nodes, log, and orphan area. Handles regular files, sparse zero blocks, symlinks, device nodes, sockets, FIFOs, directories, hard-link counting, and optional device-table-created entries.

## Dependencies
Uses `mkfs.ubifs.h`, libubi, UUID, Linux stat/ioctl flags, UBIFS media/key/LPT/compression helpers, `crc32`, and `common.h`.

## Behavior/Risks
Direct UBI output is destructive and checks whether a volume is non-empty unless `--yes` is used. The output-root containment guard canonicalizes paths but uses substring matching, so it is not a strict path-boundary check. Device-table fake stats assign `st_uid` twice where `st_gid` appears intended. The implementation is global-state-heavy, assumes stable source files during image creation, and writes the final image out of sequential order.
