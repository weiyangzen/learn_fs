# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.h

## Purpose
`probe.h` is the private structural contract for `probe.c`. It defines the probe cursor, magic-table entries, filesystem superblock layouts, byte-order helpers, and feature constants needed to identify block-device contents without mounting them.

## Important APIs, Types, and Functions
Key types are `struct blkid_probe`, `blkid_probe_t`, `struct blkid_magic`, and many packed or layout-sensitive structures for ext, XFS, Reiser, JFS, ROMFS, cramfs, swap, FAT, minix, mdraid, HFS/HFS+, OCFS/OCFS2, Oracle ASM, ISO, GFS/GFS2, NTFS, LVM2, and Btrfs. The inline helpers are `blkid_swab16()`, `blkid_swab32()`, `blkid_swab64()`, and `blkid_le*`/`blkid_be*` macros.

## Control Flow
There is no runtime control flow beyond inline byte swapping. The header supplies the exact offsets and field names that `probe.c` casts over raw buffers after a magic match.

## State, Persistence, Dependencies, Risks, and Test Signals
State is entirely caller-owned through `struct blkid_probe` and raw mapped buffers. Dependencies include `blkid/blkid_types.h`, compiler packing support, endian configuration, and architecture-specific i386 byte-swap assembly when available. Risks are high for layout drift, unaligned field access, endian mistakes, and stale filesystem formats. Test signals are successful compilation on big- and little-endian targets, `tst_types` width validation, and probe image tests that exercise labels, UUIDs, and feature flags.
