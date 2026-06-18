# File Research: sources/virtualization/spdk/module/bdev/gpt/gpt.c

## Purpose
Parses and validates GPT metadata from a bdev-read buffer, including the protective MBR, GPT header, partition-entry array location, and CRC checks.

## Main Entry Points
- `gpt_parse_mbr()` validates the protective MBR at LBA 0.
- `gpt_parse_partition_table()` validates the current primary or secondary GPT header and partition table.

## Internal Mechanics
Parsing is controlled by `gpt->parse_phase`. Primary parsing expects the header at LBA 1 and partition entries at the header-provided LBA within the front buffer. Secondary parsing expects the header at the last LBA and maps the partition array relative to the end of the loaded tail buffer.

Header validation checks header size bounds, header CRC with the CRC field zeroed, GPT signature, expected `my_lba`, and usable-LBA range. Partition validation limits entries to 128, requires SPDK's expected partition-entry struct size, locates the array, and validates the array CRC.

Protective MBR validation requires the MBR signature, a GPT protective partition entry, start LBA 1, and size either total sectors minus one or `0xFFFFFFFF`.

## Dependencies
Uses `spdk/gpt_spec.h`, SPDK endian helpers, CRC32, event/log headers, and `gpt.h`.

## Risks and Notes
The parser intentionally supports at most 128 GPT entries and one exact entry size. It mutates the in-buffer header CRC field while computing the checksum and restores it. Many validation failures are logged at debug level for probe-style use.
