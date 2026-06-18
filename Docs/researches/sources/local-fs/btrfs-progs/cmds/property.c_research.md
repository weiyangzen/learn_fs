# File Research: sources/local-fs/btrfs-progs/cmds/property.c

## Purpose

Implements the `btrfs property` command group for getting, setting, and listing supported properties on Btrfs objects.

## Commands Implemented

- `property get [-t type] <object> [name]`
- `property set [-f] [-t type] <object> <name> <value>`
- `property list [-t type] <object>`

Supported object types are device, filesystem/root, subvolume, and inode.

## Property Handlers

The `prop_handlers[]` table defines the supported properties:

- `ro`: read-only status of a subvolume.
- `label`: filesystem label for a device or filesystem root.
- `compression`: per-inode compression xattr.

## Key Helpers

- `subvolume_clear_received_uuid()` clears received-subvolume metadata through `BTRFS_IOC_SET_RECEIVED_SUBVOL`.
- `prop_read_only()` reads or changes subvolume read-only state via libbtrfsutil.
- `prop_label()` delegates label get/set to filesystem utility helpers.
- `prop_compression()` gets/sets `btrfs.compression` xattr on a path.
- `autodetect_object_types()` determines applicable object types from stat data, Btrfs fsid checks, block-device checks, subvolume inode number, and root detection.
- `check_is_root()` compares fsids between an object and its parent to decide whether a path is a filesystem root boundary.
- `setget_prop()` validates property existence, object compatibility, ambiguity, and read-only status before dispatching to a handler.
- `parse_args()` centralizes parsing of `-t` and `-f`, object/name/value positions, and type autodetection.

## Important Behavior

- Setting `ro=false` on a received read-only subvolume is blocked if `received_uuid` is set unless `-f` is used.
- With `-f`, `ro=false` also attempts to clear `received_uuid`, because leaving it set can break incremental send semantics.
- Read-write subvolumes with `received_uuid` set produce a warning.
- Missing compression xattrs are treated as an absent property rather than a hard error.
- Object type autodetection can produce multiple compatible types; if the selected property matches more than one, the user must provide `-t`.

## External Interfaces

Uses libbtrfsutil for subvolume read-only and info operations, xattr syscalls for compression, and filesystem label helpers for label get/set.
