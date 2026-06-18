# File Research: sources/local-fs/udftools/udflabel/main.c

## Role

CLI for reading or updating UDF volume identifiers in-place.

## Main Flow

- Initializes locale, `struct udf_disc`, sentinel values for optional new identifiers, and parses arguments.
- Opens the target read-only when only displaying label, or read-write exclusive when updating.
- Determines size/sector size and calls shared `read_disc()`.
- If no update is requested, decodes and prints the Logical Volume Identifier.
- For updates, validates logical volume integrity, supported write revision, partition access type, descriptor health, write-protect flags, and unsupported VAT/pseudo-overwrite cases.
- Applies requested identifier changes to in-memory descriptors.
- Recomputes descriptor CRC/checksum.
- Writes main descriptors first, syncs, writes FSD and reserve descriptors, then final `fsync()` and close.

## Important Helpers

- `get_size()` and `get_sector_size()` mirror `udfinfo`.
- `compute_crc()` and `compute_checksum()` implement descriptor integrity calculations.
- `check_desc()` validates current descriptor checksum and CRC before modifying.
- `update_desc()` updates descriptor CRC and tag checksum after modifications.
- `write_desc()` searches the discovered extent/descriptor list for the exact descriptor buffer and writes it back to the corresponding disk block unless `FLAG_NO_WRITE` is set.

## Update Coverage

Can update:

- Logical Volume Identifier in LVD, IUVD logicalVolIdent, and FSD logicalVolIdent.
- Volume Identifier in PVD.
- File Set Identifier in FSD.
- Owner, organization, and contact in IUVD implementation-use fields.
- Application Identifier and Implementation Identifier in PVD.
- UUID/VSID/full Volume Set Identifier in PVD.

## Safety and Limitations

- Refuses updates if LVID is not closed.
- Refuses UDF write revision above 2.60.
- Requires both main and reserve descriptors to be valid for PVD/LVD/IUVD updates.
- Refuses read-only, unknown, write-once, and pseudo-overwrite cases unless allowed by `--force` where implemented.
- VAT update support is explicitly not implemented for LVID/FSID changes and write-once handling.
- Does not update VAT structures for identifier changes that would require VAT-level changes.
- `--no-write` simulates and prints target blocks without writing.

## Dependencies

- Shared `read_disc()` from `../udfinfo/readdisc.h`.
- `libudffs` for UDF structures, CRC, string encoding/decoding, I/O wrappers, and endian helpers.

## Research Notes

This file is more conservative than `udfinfo`: it requires descriptor integrity checks before writes and uses exclusive open for real updates to avoid editing mounted/busy devices.
