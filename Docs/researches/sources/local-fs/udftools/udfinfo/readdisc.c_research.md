# File Research: sources/local-fs/udftools/udfinfo/readdisc.c

## Role

Shared UDF disk reader used by `udfinfo` and `udflabel`. It discovers the UDF layout, parses descriptor sequences, resolves partition mapping variants, and computes space statistics.

## Main Responsibilities

- Detect UDF block size, start block, last block, VRS, and anchor descriptors.
- Read MBR presence, anchors, main/reserve Volume Descriptor Sequences, and Logical Volume Integrity sequences.
- Select best PVD/LVD/PD/IUVD descriptors by sequence/revision rules.
- Parse sparable, virtual/VAT, and metadata partition maps.
- Resolve logical partition blocks to physical positions.
- Read sparing tables, VAT tables, metadata file maps, and File Set Descriptor.
- Set up partition extents and compute total/free blocks.

## Detection Flow

- `detect_udf()` handles explicit block size first, then logical sector size, then probes 512 through 32768.
- It tries normal first anchor, second/third anchors, and fallback anchor at sector 512.
- It uses multisession and `CDROM_LAST_WRITTEN` information when available to infer start/last positions for optical media.
- `read_vrs()` scans the Volume Recognition Sequence for BEA01, NSR02/NSR03, and TEA01, while tolerating known non-UDF descriptors such as BOOT2 and CD001.

## Descriptor Parsing

- `scan_vds()` walks main or reserve VDS extents from the selected anchor, follows nested Volume Descriptor Pointers with a cap, records extents/descriptors, and loads large LVD/USD bodies when needed.
- PVD selection chooses the smallest primary volume descriptor number and then highest volume descriptor sequence number.
- PD parsing supports up to two partition descriptors.
- LVD parsing requires UDF compliant domain identifiers and checks logical block size mismatches.
- `scan_lvis()` follows LVID sequences, stores the last parsed LVID, validates size limits, and follows next-integrity extents.

## Partition Mapping

- `find_partition()` locates type 1 or type 2 maps by identifier, partition number, or partition map index.
- `find_partition_descriptor()` resolves matching partition descriptors.
- `find_block_position()` maps:
  - Type 1 logical blocks directly.
  - Virtual partitions through VAT entries.
  - Sparable partitions through sparing table remaps.
  - Metadata partitions through metadata file or mirror file allocation maps.

## VAT and Metadata Handling

- `read_vat()` locates the VAT file near expected last/VAT block, supports FE and EFE, supports AD in ICB, short AD, and long AD forms, parses UDF 1.50 and UDF 2.00 VAT formats, updates logical volume identifiers/counts/revisions, and marks the LVID as closed once VAT is found.
- `read_metadata_file()` reads metadata file and mirror file allocation descriptors.
- `read_metadata()` locates metadata partition map and reads both metadata file maps.

## Space Accounting

- `setup_pspace()` creates PSPACE extents from partition descriptors, with overlap warnings.
- `setup_total_space_blocks()` sums one or two partition descriptor lengths.
- `count_bitmap_blocks()` counts set bits in free-space bitmaps.
- `count_table_blocks()` sums allocation descriptors in unallocated/freed space entries.
- `count_free_partition_blocks()` prefers LVID free-space table values unless VAT makes them stale, otherwise falls back to partition header bitmap/table descriptors.
- `scan_free_space_blocks()` totals free blocks over first and optional second partitions.

## Error Handling

The reader distinguishes hard failures from recoverable damage. Many malformed structures emit warnings and leave missing fields unset; only detection failure or allocation/read failures in key paths abort the full read.

## Dependencies

- `libudffs.h` for UDF structs, extent helpers, endian helpers, and no-EINTR reads.
- Linux CD-ROM ioctls for multisession and last-written information.

## Research Notes

This is the primary source of truth for existing UDF volume introspection. `udflabel` depends on its extent/descriptor records to locate blocks for in-place descriptor updates.
