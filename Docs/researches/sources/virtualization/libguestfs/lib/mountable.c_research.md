# File Research: sources/virtualization/libguestfs/lib/mountable.c

Public helpers for decomposing mountable identifiers.

Important behavior:
- `guestfs_impl_mountable_device` parses a mountable string and returns its device component.
- `guestfs_impl_mountable_subvolume` returns the btrfs subvolume component.
- If the parsed mountable has no subvolume, it reports `EINVAL` with “not a btrfs subvolume identifier”.
- Uses generated internal mountable parsing and cleanup helpers.

Filesystem relevance:
- Separates physical device and btrfs subvolume identity for mount operations and callers that need path components.
