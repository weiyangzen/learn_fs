# File Research: sources/virtualization/libguestfs/lib/available.c

## Role
Implements host-side availability checks for optional daemon feature groups.

## Main Flow
- `find_or_cache_feature()` checks `g->features` for a cached group result.
- On cache miss, calls `guestfs_internal_feature_available()` and stores the result.
- `guestfs_impl_available()` reports errors for unknown or unavailable groups.
- `guestfs_impl_feature_available()` returns boolean availability while still erroring for unknown groups.

## Result Semantics
The daemon feature result values are interpreted as available, unavailable, or unknown group.

## Filesystem/Storage Relevance
Many filesystem features depend on appliance packages or compile-time options; this file caches and exposes those capability checks.
