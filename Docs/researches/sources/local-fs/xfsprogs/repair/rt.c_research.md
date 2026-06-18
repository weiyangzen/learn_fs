# File Research: sources/local-fs/xfsprogs/repair/rt.c

Implements realtime bitmap/summary reconstruction, rt metadata inode discovery, rtgroup inode tracking, and realtime superblock checking.

Key data:
- `rtg_inodes[XFS_RTGI_MAX]`: bitmaps of discovered rt metadata inode numbers.
- `rtginodes_bad[]`: per-rt-metadata-type corruption flags.
- `struct rtg_computed`: computed realtime bitmap and summary buffers per rtgroup.
- `rt_computed`: array indexed by rtgroup.

Core flow:
- `generate_rtinfo` allocates per-rtgroup computed buffers and calls `generate_rtgroup_rtinfo`.
- `generate_rtgroup_rtinfo` walks realtime extent allocation state from repair block maps and produces bitmap words plus summary counts.
- `check_rtbitmap` and `check_rtsummary` compare computed data against existing rt metadata file contents.
- `fill_rtbitmap` and `fill_rtsummary` rewrite rt metadata file blocks from computed buffers.
- `discover_rtgroup_inodes` loads reachable rt metadata inodes before phase-3 inode clearing and records them in bitmaps.
- `unload_rtgroup_inodes` drops loaded rt metadata inodes before phase-6 rebuild.
- `mark_rtgroup_inodes_bad` releases a metadata type across all rtgroups and marks it for rebuild.
- `check_rtsb` reads the realtime superblock and rewrites it if invalid and modification is allowed.
- `rewrite_rtsb` updates the realtime superblock from the primary filesystem superblock.

Important behavior:
- Supports both old sb-rooted realtime bitmap/summary files and newer rtgroup metadata.
- Realtime bitmap word layout differs for rtgroups versus older filesystems; helpers abstract endian/layout writes.
- For rtgroups, metadata block owner headers are checked while validating rt files.
- Missing or unloadable sb-rooted rt files set `need_rbmino` or `need_rsumino` so later phases can recreate them.
