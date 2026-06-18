# File Research: sources/virtualization/nbdkit/plugins/partitioning/partition-gpt.c

## Purpose
Creates GPT metadata for the partitioning plugin, including protective MBR, primary/backup GPT headers, partition entry arrays, CRCs, and GUID parsing.

## Main Entry Points
- `create_gpt_layout()` populates primary and secondary GPT regions.
- `create_gpt_partition_header()` writes GPT headers with usable LBA bounds, entry metadata, and CRCs.
- `create_gpt_partition_table()` emits one GPT entry per file region.
- `create_gpt_partition_table_entry()` writes partition type GUID, unique GUID, LBA range, boot attribute, and optional ASCII filename as UTF-16LE name.
- `create_gpt_protective_mbr()` creates the protective MBR partition.
- `parse_guid()` validates and converts textual GPT GUIDs into on-disk byte order.

## Dependencies
Uses common GPT definitions, EFI CRC32, byte swapping, ASCII/hexdigit helpers, regions, and virtual-disk globals.

## Risks and Notes
Partition names may expose server-side filenames to clients when filenames are short 7-bit ASCII. Random unique GUIDs are generated elsewhere without enforcing RFC GUID version/variant bits. GPT CRC and LBA calculations assume the virtual region layout is sector-aligned.
