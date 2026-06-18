# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/gpt.c

## Purpose
Implements GPT reading, validation, printing, recovery, initialization, editing helpers, and writing.

## Key Behavior
- Maintains global GPT state: protective MBR `gmbr`, header `gh`, and partition array `gp`.
- Converts GPT UTF-16LE partition names to/from simple ASCII strings.
- `gpt_chk_mbr()` and `protective_mbr()` validate the protective MBR with a single EFI/GPT partition.
- `get_header()` reads and validates a GPT header:
  - signature and revision
  - self LBA
  - header/entry sizes
  - partition count
  - header CRC
  - usable LBA range
  - partition table location
  - GUID decoding
- `get_partition_table()` reads partition entries, verifies CRC, decodes little-endian UUIDs and numeric fields.
- Accepts wrong-endian CRCs as a compatibility concession.
- `GPT_recover_partition()` either recovers from existing GPT structures or parses printed partition lines, UUID lines, and attributes lines.
- `GPT_read()` reads protective MBR plus primary/secondary/any GPT and clears state if invalid.
- `GPT_print()` prints usable LBA range, disk GUID in verbose mode, sorted partitions, and free ranges.
- `GPT_print_part()` prints type, start/size, optional GUID/name, and decoded attributes.
- `add_partition()` places a partition in the largest free range with `BLOCKALIGNMENT`.
- `init_gh()` creates a protective MBR and primary GPT header defaults.
- `init_gp()` creates EFI system and OpenBSD area partitions, preserving protected/required entries when only regenerating partition entries.
- `GPT_zap_headers()` clears primary and secondary GPT headers when switching to MBR.
- `GPT_write()` writes protective MBR, primary header/table, secondary header/table, recomputes CRCs, and reloads the kernel disklabel via `DIOCRLDINFO`.
- `sort_gpt()` and `lba_free()` compute sorted partitions and the largest free LBA span.
- `GPT_get_lba_start()`, `GPT_get_lba_end()`, and `GPT_get_name()` are interactive field editors.
- `crc32()` is a local GPT CRC implementation adapted from Hacker’s Delight.

## Notes
The module is conservative about protected/required GPT entries and validates both primary and secondary layouts against disklabel-derived disk size.
