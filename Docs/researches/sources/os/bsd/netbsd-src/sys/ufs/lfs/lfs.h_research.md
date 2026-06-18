# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs.h

Read completely: 1518 lines.

Defines NetBSD LFS public on-disk formats, mount/userland control ABI, in-memory filesystem state, segment structures, and shared constants.

Core layout and constants:
- Defines fixed layout values such as label/superblock padding, reserved inode numbers, root/whiteout inode numbers, summary size defaults, name length, direct/indirect address counts, and directory block sizing.
- Documents LFS directory entry format, including 32-bit vs 64-bit headers, record padding, old directory format compatibility, and d_type/namlen interpretation.
- Defines file type constants matching inode mode high bits and directory entry type codes.
- Uses compile-time assertions to lock structure sizes and alignment.

On-disk metadata:
- Provides 32-bit and 64-bit directory headers/templates.
- Provides `struct lfs32_dinode`, `struct lfs64_dinode`, and `union lfs_dinode`, including direct/indirect block arrays and metadata fields such as times, uid/gid, generation, flags, sizes, block counts, and modrev.
- Defines segment usage structures (`SEGUSE`, `SEGUSE_V1`) and segment flags for active, dirty, superblock-bearing, error, empty, invalid, and reclaim-ready segments.
- Defines segment-summary file info (`FINFO32`, `FINFO64`), inode-info (`IINFO32`, `IINFO64`), ifile entries (`IFILE32`, `IFILE64`, v1), cleaner info, and segment summaries (`SEGSUM_V1`, `SEGSUM32`, `SEGSUM64`).
- Defines 32-bit and 64-bit disk superblocks (`struct dlfs`, `struct dlfs64`) with checkpoint fields, geometry, cleaner metadata, superblock locations, serial/timestamp, mount path, and checksum.

In-memory and kernel-facing state:
- `struct lfs` wraps the disk superblock union and mount-time flags for 64-bit, byte-swapped, and old-directory formats.
- Runtime state tracks current segment writing, ifile vnode, preventative/segment/fragment/ifile locks, writer/dirop counters, dirty inode counts, active superblock selection, cleaner state, reserved blocks, vnode chains, pending segment accounting, device vnode/dev_t, ULFS geometry, quota2 placeholders, and autocleaner state.
- `struct segment` describes a segment under construction, including buffer arrays, summary pointers, inode buffers, file info, bytes remaining, segment number, flags, and I/O counters.

Userland/control ABI:
- Defines `BLOCK_INFO` and compatibility versions for older binaries.
- Defines fcntl/private commands for rewind, invalidation, resize, wrap control, ifile file handle retrieval, segment waits, cleaner info, segment usage, bmapv/markv, reclaim, file stats, file rewrite/scramble, segment rewrite, and autoclean control.
- Provides maximum counts for segment usage, markv blocks, file stats, and rewrite arrays.
- Defines `struct ulfs_args` for mounting.

Risks and notes:
- This file is a dense ABI boundary shared by kernel, tools, and cleaners; field-size changes are high risk.
- The file carries substantial compatibility for LFS v1, 32-bit LFS, 64-bit LFS, older userland ABIs, and old directory formats.
- Multiple comments identify legacy or questionable behavior, including old directory format retention, strict-aliasing concerns around v1 ifile entries, and diagnostic segment-lock assertions that log rather than enforce.
