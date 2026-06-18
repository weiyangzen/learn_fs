# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskgpt.c

GPT partition-table reader used when the MBR parser detects a protective GPT MBR entry.

Key responsibilities:
- Reads the primary GPT header at LBA 1 and validates header size and header CRC.
- Validates partition entry count, entry size, entry table location, and table size against media bounds.
- Reads the GPT entry table and replaces the caller's minimal slice structure with one sized for up to 128 GPT entries plus special slices.
- Converts little-endian GPT UUIDs, LBAs, attributes, and UTF-16 name fields into host-order temporary entries.
- Maps non-empty GPT entries into DragonFly disk slices, including storage/type UUIDs and offsets/sizes.
- Maps known DragonFly and FreeBSD GPT type UUIDs to legacy DOS partition type values for downstream BSD-label probing.

Important behavior:
- GPT parsing is not recursive; once GPT is detected the rest of the MBR is ignored.
- GPT entry 0 is exposed through `COMPATIBILITY_SLICE` (`s0`), and later GPT entries are mapped starting at `BASE_SLICE`.
- Entries overlapping the GPT table, beyond media bounds, or with inverted LBA ranges are rejected with diagnostics.

Dependencies:
- Depends on `sys/gpt.h`, UUID helpers, disk slice structures, buffer/BIO synchronous reads, and `crc32()`.

Notable risks:
- Only the primary GPT path is handled here; backup GPT recovery is not implemented in this routine.
- The GPT entry-array CRC from the header is not checked, so validation is weaker than full GPT verification.
- The implementation caps GPT entries at 128 and expects the whole entry table read to fit in one pbuf-sized request.
