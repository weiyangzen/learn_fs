# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.h

## Purpose

Defines kernel-only ATTRI/ATTRD log item structures and the public helper for adding deferred attr operations.

## Key Types

- `struct xfs_attri_log_nameval`
  - shared name/value/new-name/new-value storage
  - refcounted lifetime
- `struct xfs_attri_log_item`
  - attr intent log item
  - refcount
  - shared name/value pointer
  - on-disk log format
- `struct xfs_attrd_log_item`
  - attr done log item
  - pointer to the related ATTRI
  - done log format
- `enum xfs_attr_defer_op`
  - set
  - remove
  - replace

## Main API

- `xfs_attr_defer_add`

## Research Notes

This header is used by the attr layer to queue replayable xattr work and by log recovery to manage ATTRI/ATTRD items.
