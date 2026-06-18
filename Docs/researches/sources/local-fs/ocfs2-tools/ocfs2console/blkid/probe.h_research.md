# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.h

Defines probe table metadata, on-disk structure slices, OCFS/OCFS2 layouts, Oracle ASM label layout, ISO descriptor layout, and byte-swap helpers.

Key contents:
- `struct blkid_magic`
  - Filesystem type, kilobyte offset, byte offset, magic length, magic bytes, optional probe callback.
- Probe callback typedef `blkid_probe_t`.
- Partial on-disk structures for:
  - ext2/ext3 superblock
  - XFS superblock
  - ReiserFS superblock
  - JFS superblock
  - ROMFS superblock
  - swap header
  - VFAT/MSDOS boot sectors
  - Minix superblock
  - MD RAID superblock
  - HFS superblock
  - OCFS volume header/label
  - OCFS2 superblock
  - Oracle ASM disk label
  - ISO volume descriptor
- OCFS helpers:
  - `ocfsmajor`
  - `ocfslabellen`
  - `ocfsmountlen`
- Endian helpers:
  - `blkid_swab16`, `blkid_swab32`, `blkid_swab64`
  - `blkid_le*` and `blkid_be*` macros

Notable details:
- Structures are intentionally partial: only fields needed for type/label/UUID probing are represented.
- Contains x86 inline assembly byte-swap fast paths for older GCC/i386 builds.
- OCFS2 superblock signature and supported block size constants are duplicated locally for probing.
