# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_info.c

## Purpose

Provides debug/stat reporting for XFS zoned allocation state.

## Main Responsibilities

- Converts write lifetime hints to short strings.
- Prints open-zone state including write pointer, written count, used blocks, hint, and GC marker.
- Prints distribution of fully written reclaimable zones by used-block bucket.
- Prints zoned free counters, reservation state, GC-needed state, zone counts, and open-zone counts.

## Important Invariants

- Open-zone list output is protected by `zi_open_zones_lock`.
- Used-bucket distribution output is protected by `zi_used_buckets_lock`.
- “100%” bucket is derived from total zones minus free/open/GC/reclaimable zones.

## Dependencies

Uses seq_file, XFS free counters, zoned allocator private state, realtime group/rmap state, and GC need checks.

## Research Notes

This file is observability-only and helps diagnose allocator/GC pressure and zone placement behavior.
