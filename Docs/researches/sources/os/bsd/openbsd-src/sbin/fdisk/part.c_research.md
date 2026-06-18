# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/part.c

Implements fdisk partition type lookup, display, and conversion helpers for both MBR and GPT partition tables.

Major contents:
- Defines known MBR partition type IDs and descriptions, with OpenBSD, BSD, DOS/FAT, Linux, EFI, Solaris, macOS, Plan 9, and many legacy IDs.
- Defines known GPT partition type GUID constants and `gpt_types`, including OpenBSD, EFI system, Microsoft basic data, Linux, BSD, macOS/APFS, ChromeOS kernel, and protected platform/firmware partitions.
- Defines the user-facing partition type menu table shared by MBR and GPT prompts.
- Provides menu filtering/printing for MBR-only and GPT-capable partition types.
- Maps between MBR IDs, GPT GUIDs, menu names, and short hexadecimal menu IDs.

Conversion and validation behavior:
- `PRT_dp_to_prt` converts on-disk DOS partition entries into internal `struct prt`, including extended-MBR offset rules and EFI protective size handling.
- `PRT_prt_to_dp` converts internal partitions back to MBR disk entries, calculating CHS fields and LBA start/size fields.
- `PRT_lba_to_chs` converts LBA ranges into CHS tuples using current disk geometry.
- `chs_to_dp` clamps out-of-range CHS values to force LBA-style interpretation.
- `PRT_print_part` prints one MBR partition and warns if it starts or extends beyond disk size.
- `PRT_uuid_to_desc` and `PRT_desc_to_guid` translate GPT UUIDs to display/menu identifiers and parse names, GUID strings, or menu IDs back to GUIDs.
- `PRT_protected_uuid` protects selected GPT partition types from modification, with extra EFI system protection when protected EFI-dependent GPT types are present.

This file is the central fdisk partition-type knowledge base and the bridge between on-disk MBR/GPT identifiers and interactive user-facing names.
