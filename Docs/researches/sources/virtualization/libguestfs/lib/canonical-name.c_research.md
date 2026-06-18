# File Research: sources/virtualization/libguestfs/lib/canonical-name.c

## Role
Implements canonicalization of device names for public API callers.

## Main Logic
- Converts simple `/dev/hd*`, `/dev/vd*`, and similar disk names to `/dev/sd*` style while avoiding LVs and `/dev/md`.
- For `/dev/mapper/*` and `/dev/dm-*`, tries `guestfs_lvm_canonical_lv_name()`.
- Suppresses errors from LVM canonicalization and returns the original string on failure, preserving historical API behavior.

## Filesystem/Storage Relevance
Canonical device naming affects how callers correlate guest block devices, LVs, and filesystem mount targets.
