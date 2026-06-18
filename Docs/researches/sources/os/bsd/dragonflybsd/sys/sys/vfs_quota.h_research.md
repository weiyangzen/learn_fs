# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfs_quota.h

## Summary
VFS quota control and write-admission declarations.

## Main Responsibilities
- Declares mount quota init/done helpers.
- Declares `vquotactl()` property-list control entry point.
- Exposes `vfs_quota_enabled`.
- Declares vnode-to-mount helper for kernel structures.
- Declares `vq_write_ok()` for uid/gid/delta write checks.

## Important Behavior
The interface uses proplib `plistref` for quota control data and attaches quota lifecycle to `struct mount`.

## Risks
Quota enforcement depends on callers checking write deltas consistently. Missing calls around metadata or delayed allocation paths could bypass accounting.
