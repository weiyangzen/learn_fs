# File Research: sources/virtualization/libguestfs/daemon/uuids.c

## Role
Dispatches UUID-setting requests to filesystem-specific implementations.

## Main Operations
- `do_set_uuid()` reads the device filesystem type via `get_blkid_tag(device, "TYPE")`.
- Ext filesystems are handled through `do_set_e2uuid()` after rejecting ext magic UUID strings.
- XFS, swap, and btrfs are dispatched through a small handler table.
- `do_set_uuid_random()` generates a UUID and dispatches ext, XFS, btrfs, or swap-specific randomization.

## Validation
- Ext rejects `clear`, `random`, and `time` for the generic fixed-UUID API.
- XFS rejects `nil` and `generate` for fixed UUIDs.
- Unsupported filesystem types produce `NOT_SUPPORTED`.

## Filesystem/Storage Relevance
This file coordinates persistent filesystem identity metadata across ext, XFS, swap, and btrfs.
