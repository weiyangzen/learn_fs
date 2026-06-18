# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rtgroup.h

## Purpose

Defines the in-core realtime group structure and inline helpers for realtime group reference management, geometry, address conversion, metadata inode access, and rtgroup locking APIs.

## Main Types

- `enum xfs_rtg_inodes`
  - `XFS_RTGI_BITMAP`
  - `XFS_RTGI_SUMMARY`
  - `XFS_RTGI_RMAP`
  - `XFS_RTGI_REFCOUNT`
- `struct xfs_rtgroup`
  - embeds `struct xfs_group`
  - stores per-rtgroup metadata inodes
  - stores realtime extent count
  - stores either realtime summary cache or open-zone state
  - tracks zoned GC operations through `rtg_gccount`

## Main Helpers

- Structure conversion:
  - `to_rtg`
  - `rtg_group`
  - `rtg_mount`
  - `rtg_rgno`
  - `rtg_blocks`
- Metadata inode access:
  - `rtg_bitmap`
  - `rtg_summary`
  - `rtg_rmap`
  - `rtg_refcount`
- Rtgroup references:
  - passive: `xfs_rtgroup_get`, `xfs_rtgroup_hold`, `xfs_rtgroup_put`
  - active: `xfs_rtgroup_grab`, `xfs_rtgroup_rele`
  - iteration: `xfs_rtgroup_next_range`, `xfs_rtgroup_next`
- Address conversion:
  - realtime block to group/block
  - group block to realtime block
  - realtime block to disk address
  - disk address to realtime block

## Important Invariants

- `XFS_RTG_FREE` marks free rtgroups for zoned allocation.
- `xfs_verify_rgbno` and `xfs_verify_rgbext` assert that rtgroups are enabled.
- `xfs_rtx_to_rgbno` uses fast shifting when realtime extent size is a power of two.
- `xfs_rtb_to_daddr` and `xfs_daddr_to_rtb` account for rtgroup layouts with or without disk-address gaps.

## Conditional Behavior

When `CONFIG_XFS_RT` is disabled, most rtgroup operations become no-op or unsupported stubs. Inline conversion helpers remain available for build compatibility.

## Research Notes

This header is the primary API surface for realtime group consumers. It is also where zoned realtime state begins to diverge from bitmap-backed realtime state.
