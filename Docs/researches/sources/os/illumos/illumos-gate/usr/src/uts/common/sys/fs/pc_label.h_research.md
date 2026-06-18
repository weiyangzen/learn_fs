# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_label.h

This header defines PC master boot block, partition, DOS/FAT identifier, media descriptor, sector-size, and endian conversion constants.

Boot block and partition offsets:
- Defines offsets for BPB fields such as bytes per sector, sectors per cluster, reserved sectors, FAT count, root entries, sector count, media byte, sectors per FAT, geometry, and hidden sectors.
- Partition table starts at `0x1be` with four entries.
- FAT type-string offsets differ for FAT12/16 and FAT32.
- BPB starts at `0xb`; DOS signature is at `0x1fe`.

Partition and FAT identifiers:
- DOS partition system indicators cover FAT12, FAT16, huge FAT16, FAT32, FAT32 LBA, and FAT16 LBA variants.
- Defines maximum sector/cluster thresholds for FAT12.
- Jump opcodes and DOS signature constants are defined.

Media descriptors:
- Includes fixed disk and common floppy media descriptor byte values.
- Comment notes media-descriptor identification is unreliable.
- PC filesystem sector size constant is 512.

Endian helpers:
- On little-endian systems, `ltohs`, `ltohi`, `htols`, and `htoli` direct-reference storage.
- On big-endian systems, helpers assemble values by byte extraction.

Dependencies and relationships:
- Older/low-level companion to `pc_fs.h` BPB parsing.
- Provides partition and media constants used by PCFS mounting and validation paths.
