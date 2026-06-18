# File Research: sources/virtualization/libblockdev/src/plugins/btrfs.h

## Role
Public header for the Btrfs libblockdev plugin.

## Constants and Errors
- Defines `BD_BTRFS_MAIN_VOLUME_ID` as `5`.
- Defines `BD_BTRFS_MIN_MEMBER_SIZE` as `128 MiB`.
- Declares `BD_BTRFS_ERROR` and `BDBtrfsError` values:
  - technology unavailable;
  - device error;
  - parse error.

## Data Structures
- `BDBtrfsDeviceInfo`: device id, path, size, used bytes.
- `BDBtrfsSubvolumeInfo`: subvolume id, parent id, path.
- `BDBtrfsDeviceStats`: device id, path, and Btrfs error counters.
- `BDBtrfsFilesystemInfo`: label, UUID, number of devices, used bytes.
- Declares copy/free helpers for each struct.

## Technology Model
- `BDBtrfsTech` categories:
  - filesystem;
  - multi-device;
  - subvolume;
  - snapshot.
- `BDBtrfsTechMode` bit flags:
  - create;
  - delete;
  - modify;
  - query;
  - delete recursive.

## Public Operations
Declares plugin lifecycle and availability calls plus Btrfs operations for:
- volume creation and mkfs;
- adding/removing devices;
- subvolume create/delete/delete-recursive/list/default-id/default-set;
- snapshot creation;
- filesystem info, resize, check, repair, label change;
- device stats.

## Dependencies and Interactions
- Includes GLib, GObject, and `blockdev/utils.h` for types and `BDExtraArg`.
- Implemented by `btrfs.c`.
- Built and installed conditionally by `src/plugins/Makefile.am`.

## Filesystem/Storage Relevance
This header defines libblockdev's public Btrfs administration surface for consumers and bindings.
