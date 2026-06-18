# File Research: sources/os/linux/linux/block/partitions/efi.c

## Summary
Implements EFI GPT partition-table detection, validation, and partition export.

## Main Responsibilities
- Handles the `gpt` kernel command-line override.
- Validates protective and hybrid MBRs.
- Reads GPT headers and partition entry arrays.
- Verifies GPT signatures, sizes, usable LBA ranges, and CRCs.
- Chooses primary or alternate GPT when one is invalid.
- Emits Linux partition entries with GPT UUID/name metadata.

## Key APIs
- `efi_partition()`.
- Internal helpers: `find_valid_gpt()`, `is_gpt_valid()`, `is_pmbr_valid()`, `alloc_read_gpt_header()`, `alloc_read_gpt_entries()`.

## Important Behavior
Without `gpt`, the parser requires a valid protective or hybrid MBR before accepting GPT data. With `gpt`, it may try alternate GPT locations even if the protective MBR path fails, including a disk-driver-provided `alternative_gpt_sector()`.

Header validation checks GPT signature, header size bounds, header CRC, `my_lba`, usable LBA bounds, partition entry size, partition entry allocation size, and partition-entry-array CRC.

`efi_partition()` maps GPT logical blocks to 512-byte kernel sectors, skips empty or out-of-range entries, marks Linux RAID GUID entries for md autodetect, stores partition GUID in `info->uuid`, and converts UTF-16LE partition names to printable 7-bit labels.

## State and Lifetime
GPT headers and entry arrays are dynamically allocated during scan and freed before return. Disk reads use `read_lba()`, which internally reads 512-byte sectors through the partition core.

## Risks
The UTF-16 partition name conversion is intentionally lossy. GPT validity depends on correct logical block sizing and CRC coverage; malformed tables can be ignored even when some entries look plausible.
