# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uuid.h

## Role

Defines UUID wire/storage types and endian conversion helper.

## Key Interfaces

- `uuid_node_t` stores a 6-byte node ID.
- `struct uuid` stores RFC-style UUID fields: time low/mid/high-version, clock sequence bytes, and 6-byte node address.
- Defines `UUID_LEN` as 16 and printable string length as 37.
- Defines `uuid_t` as a 16-byte `uchar_t` array.
- `UUID_LE_CONVERT(dest, src)` copies a UUID struct and converts time fields to little-endian using `LE_32`/`LE_16`.

## Risk Notes

UUID byte order is frequently confused between struct and byte-array forms. The conversion macro only adjusts the integer time fields, leaving sequence/node bytes unchanged.
