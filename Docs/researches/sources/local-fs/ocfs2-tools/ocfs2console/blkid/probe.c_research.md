# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/probe.c

Core content-signature probing implementation for the bundled blkid library.

Key responsibilities:
- Reads known offsets from block devices.
- Matches filesystem or volume-manager magic values.
- Extracts TYPE, LABEL, UUID, and selected secondary tags.
- Verifies cached devices and drops stale/invalid entries.

Supported signatures include:
- Oracle ASM
- NTFS
- JBD, ext2, ext3
- ReiserFS variants
- VFAT/FAT12/FAT16/FAT32
- Minix, VxFS, XFS, ROMFS, BFS, cramfs, QNX4
- UDF and ISO9660
- JFS, HFS, UFS, HPFS, SysV
- swap variants at multiple page-size offsets
- OCFS and OCFS2
- MD RAID superblock at end of device

Key functions:
- `check_mdraid`
  - Reads MD superblock near end of device and reconstructs MD UUID.
- `set_uuid`
  - Converts binary UUID to text and sets `UUID`.
- Filesystem-specific probe helpers:
  - `probe_ext2`, `probe_ext3`, `probe_jbd`
  - `probe_vfat`, `probe_msdos`
  - `probe_xfs`, `probe_reiserfs`, `probe_jfs`, `probe_romfs`
  - `probe_swap0`, `probe_swap1`
  - `probe_udf`
  - `probe_ocfs`, `probe_ocfs2`
  - `probe_oracleasm`
- `blkid_verify(cache, dev)`
  - Revalidates a device path.
  - Throttles reprobes.
  - Opens and stats the device.
  - Tries current cached type first, then all known signatures if current type fails.
  - Sets `TYPE`, `LABEL`, `UUID`, `SEC_TYPE`, `MOUNT` as applicable.
- `blkid_known_fstype(fstype)`
  - Checks whether a type appears in the signature table.

OCFS-specific details:
- `probe_ocfs` reads OCFS v1 label/header layout, sets:
  - `SEC_TYPE=ocfs1` for major 1
  - `SEC_TYPE=ntocfs` for major >= 9
  - `LABEL`, `MOUNT`, `UUID`
- `probe_ocfs2` recognizes `OCFSV2` signatures at 1K, 2K, 4K, and 8K offsets, then sets `LABEL` and `UUID`.

Notable details:
- Cached 1 KiB buffers are indexed by probe offset to avoid duplicate reads.
- If a cached type no longer matches, stale type/label/UUID tags are cleared and probing restarts.
- If probing cannot find any type and no old type remains, the device cache entry is freed.
- File descriptor leak risk: paths returning early after successful open, such as some stale-device branches, do not always close before returning.
