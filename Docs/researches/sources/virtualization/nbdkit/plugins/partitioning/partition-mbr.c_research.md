# File Research: sources/virtualization/nbdkit/plugins/partitioning/partition-mbr.c

## Purpose
Creates MBR and extended boot record layouts for the partitioning plugin.

## Main Entry Points
- `create_mbr_layout()` writes the primary MBR and, when needed, a chain of EBRs for more than four files.
- `find_file_region()` and `find_ebr_region()` locate previously constructed virtual regions.
- `create_mbr_partition_table_entry()` writes a 16-byte MBR partition table entry with boot flag, CHS placeholders, partition ID, start sector, and sector count.

## Internal Mechanics
For up to four files, each file becomes a primary partition. For more than four files, the first three files are primary partitions, the fourth MBR entry is an extended partition, and files from index 3 onward are logical partitions linked through EBR sectors.

## Dependencies
Uses byte swapping, alignment/rounding helpers, regions, and virtual-disk globals.

## Risks and Notes
CHS fields are always saturated to a large placeholder value, so LBA fields are authoritative. The code relies on earlier config validation to prevent MBR sector fields exceeding `UINT32_MAX`.
