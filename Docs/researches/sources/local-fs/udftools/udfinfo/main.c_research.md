# File Research: sources/local-fs/udftools/udfinfo/main.c

## Role

Read-only CLI frontend that opens a UDF device/image, invokes the shared reader, and prints normalized filesystem metadata.

## Main Flow

- Sets `appname` and locale.
- Allocates initial `USPACE` extent and initializes `struct udf_disc`.
- Parses block/start/last/VAT/charset options.
- Opens target with `O_RDONLY|O_EXCL`, falling back to non-exclusive read with a warning if busy.
- Determines byte size and logical sector size.
- Calls `read_disc()`.
- Selects primary/reserve LVD/PVD/PD/IUVD descriptors.
- Computes used/free/behind blocks and Windows-style serial number.
- Extracts UUID and remaining VSID from PVD Volume Set Identifier.
- Prints key-value metadata and discovered non-free extents.

## Printed Metadata

Includes filename, label, uuid, lvid, vid, vsid, fsid, fullvsid, owner, organization, contact, appid, impid, Windows serial number, block counts, file/dir counts, UDF revisions, start/last/VAT block, integrity state, access type, write-protect flags, and typed extent locations.

## Important Helpers

- `get_size()` uses `BLKGETSIZE64`, regular file size, or seek-to-end fallback.
- `get_sector_size()` uses `BLKSSZGET` and validates UDF-compatible powers of two.
- `compute_windows_serial_num()` sums FSD bytes into four checksum lanes.
- `compute_behind_blocks()` counts trailing blocks beyond the last non-free extent.
- `print_dstring()` decodes OSTA Unicode dstrings with newline normalization.
- `print_astring()` converts fixed 7-bit ASCII identifiers into dstring form for common printing.
- `dump_space()` prints non-free/non-reserved extents.

## Dependencies

- Shared UDF parser in `readdisc.c`.
- `libudffs` string, endian, extent, and read helpers.
- Linux block-device ioctls.

## Research Notes

This file does not deeply validate descriptors itself; it relies on `read_disc()`. It is a useful reference for how callers consume the populated `struct udf_disc`.
