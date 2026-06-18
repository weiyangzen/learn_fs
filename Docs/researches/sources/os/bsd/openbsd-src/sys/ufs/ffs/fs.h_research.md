# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/fs.h

Read completely: 591 lines.

Defines the on-disk and in-memory FFS superblock/cylinder-group layout plus address, size, fragment, and geometry macros used by FFS and UFS code.

Core definitions:
- Declares boot/superblock locations and search offsets, block/fragment limits, mount and volume name sizes, default free-space and allocation tuning constants, snapshot reservation count, and clean/flag magic values.
- `struct fs` is the FFS superblock, containing geometry, block/fragment sizing, cylinder group layout, summary counters, mount metadata, compatibility fields, UFS1/UFS2 extended state, flags, max file size, and embedded variable layout data.
- `struct cg` and legacy `struct ocg` describe cylinder-group headers, free maps, inode maps, rotational summaries, cluster summaries, and compatibility layout.
- Provides macros for summary access, cylinder-group address calculation, inode-to-block mapping, block/fragments conversions, offsets/rounding, available-space calculation, block size at logical block, sectors per block/fragment, indirect count, and kernel max file size.

Integration and risks:
- This is a filesystem ABI header; structure field order and exact widths are part of on-disk compatibility.
- Many macros assume power-of-two block/fragment sizes and valid superblock-derived masks/shifts.
- `blksize()`, `dblksize()`, and `sblksize()` are relied on by read/write/truncate paths to avoid over-reading partial final fragments.
