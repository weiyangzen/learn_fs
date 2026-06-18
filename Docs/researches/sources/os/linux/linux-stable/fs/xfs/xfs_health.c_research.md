# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_health.c

## Purpose

Implements XFS health state tracking for filesystem-wide metadata, allocation groups, realtime groups, and inodes. It records sick/corrupt/healthy state and translates internal health masks to ioctl-visible health fields.

## Main Responsibilities

- Warns at unmount if uncorrected metadata errors remain.
- Special-cases unhealthy filesystem counters at unmount to avoid encouraging repair on a dirty log.
- Marks filesystem metadata:
  - sick
  - corrupt and checked
  - healthy and checked
  - sampled
- Marks group metadata for AGs and rtgroups:
  - sick
  - corrupt and checked
  - healthy and checked
  - sampled
- Provides raw AG/rtgroup number wrappers:
  - `xfs_agno_mark_sick`
  - `xfs_rgno_mark_sick`
- Marks inode metadata:
  - sick
  - corrupt and checked
  - healthy and checked
  - sampled
- Reports metadata errors through fserror/fsnotify paths, using file-specific reporting for normal inodes and metadata reporting for internal or reclaim/new inodes.
- Prevents sick inodes from being discarded from cache by clearing `I_DONTCACHE`.
- Converts internal health masks to ioctl masks for:
  - filesystem geometry
  - AG geometry
  - rtgroup geometry
  - bulkstat
  - health monitor events
- Marks bmap, btree, dir/attr, and da metadata sick from lower-level corruption observations.

## Important Invariants

- Each health domain validates masks against its allowed sick bits.
- Clearing primary sickness also clears secondary sickness in filesystem, group, and inode domains.
- `checked` bits record that metadata was examined, regardless of whether it remains sick.
- Ephemeral in-memory btrees do not get persistent health state.
- Parent-pointer corruption discovered during handle parent enumeration marks the inode parent health bit sick.

## Dependencies

- Uses mount, group, rtgroup, inode locks for health state serialization.
- Uses tracepoints, fserror reporting, and `xfs_healthmon`.
- Integrates with geometry, bulkstat, btree, bmap, dir/attr, and daemon attribute paths.

## Research Notes

This file centralizes health accounting and user-visible health translation. It is not a scrubber itself; it records and reports observations made elsewhere and keeps enough state for ioctl users, health monitors, and unmount warnings.
