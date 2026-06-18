# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/partition-gpt.c

This file creates the GPT metadata and protective MBR for the linuxdisk plugin.

Key behavior:
- `create_partition_table` fills protective MBR, GPT partition entries, primary GPT header, and secondary GPT header.
- Protective MBR creates a partition type `0xee` covering the disk or the maximum MBR-representable span.
- GPT headers use standard signature/revision, primary/backup LBA fields, usable LBA range, partition entry location, and CRCs.
- The partition table contains one Linux filesystem partition for the region of type `region_file`.
- Partition type GUID is Linux filesystem data: `0FC63DAF-8483-4772-8E79-3D69D8477DE4`.
- Partition attributes set bit value `4` when marked bootable.

Dependencies:
- Uses common GPT structs/constants, EFI CRC32, byte swapping, alignment, rounding, and regions helpers.
- Consumes `disk->regions` and `disk->guid` created in `virtual-disk.c`.

Risks:
- The unique partition GUID is raw random bytes generated elsewhere and comments note it may not follow GUID conventions.
- Assumes exactly one `region_file` partition region.
