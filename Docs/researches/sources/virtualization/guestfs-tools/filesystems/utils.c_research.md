# File Research: sources/virtualization/guestfs-tools/filesystems/utils.c

Shared helper for `virt-filesystems` and `virt-inspector`.

Function:
- `get_filesystem_version(guestfs_h *g, const char *dev, const char *fs_type)`

Current implementation:
- Only handles XFS when `GUESTFS_HAVE_XFS_INFO2` is available.
- Calls `guestfs_xfs_info2`.
- Reads `meta-data.crc`:
  - `0` maps to XFS version `"4"`.
  - `1` maps to XFS version `"5"`.
- Suppresses libguestfs errors during optional probing.
- Returns `NULL` when version is unknown.

Research relevance: small filesystem feature probe used to enrich reporting without making unsupported version detection fatal.
