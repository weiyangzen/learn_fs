# File Research: sources/virtualization/libblockdev/src/plugins/fs/btrfs.h

## Role

`btrfs.h` is the public API header for filesystem-plugin Btrfs operations.

## Public API

It declares `BDFSBtrfsInfo` with label, UUID, size, and free-space fields, plus copy/free helpers.

Operations include:

- mkfs
- check
- repair
- set/check label
- set/check UUID
- get info
- resize

## Dependencies

The header includes GLib and libblockdev utility types, mainly for `BDExtraArg`.

## Notable Risks

The API is for simple single-device Btrfs filesystem operations. The implementation rejects multi-device query/resize and documents that more complex setups belong to the dedicated Btrfs plugin.
