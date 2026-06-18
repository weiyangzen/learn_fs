# File Research: sources/virtualization/libblockdev/src/plugins/fs/exfat.h

## Role

`exfat.h` is the public API header for filesystem-plugin exFAT operations.

## Public API

It declares `BDFSExfatInfo`, containing label, UUID, sector size, sector count, and cluster count.

Operations include:

- mkfs
- check
- repair
- set/check label
- set/check UUID
- get info

There is no resize API in this header.

## Dependencies

The header includes GLib and libblockdev utility types for `BDExtraArg`.

## Notable Risks

The UUID exposed here is an exFAT 32-bit volume ID represented as a string, not an RFC-4122 UUID.
