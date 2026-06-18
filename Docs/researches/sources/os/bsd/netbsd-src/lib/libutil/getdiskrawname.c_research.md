# File Research: sources/os/bsd/netbsd-src/lib/libutil/getdiskrawname.c

## Purpose
Converts between NetBSD block-device “cooked” disk names and character-device raw disk names.

## Key Details
- `getdiskrawname` requires the input to stat as a block device, then constructs the raw path.
- `getdiskcookedname` requires the input to stat as a character device, then constructs the cooked path.
- Resolves symlinks, preserving relative symlink directory context.
- Special-cases ZFS zvol paths under `/dev/zvol/dsk` and `/dev/zvol/rdsk`.
- Normal paths insert or remove the leading `r` from device basenames.

## Dependencies and Role
- Important storage/device naming helper used by tools that need the correct block or raw device node.
