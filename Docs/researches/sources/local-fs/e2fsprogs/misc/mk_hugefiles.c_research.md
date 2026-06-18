# File Research: sources/local-fs/e2fsprogs/misc/mk_hugefiles.c

`mk_hugefiles.c` implements optional creation of large preallocated regular files during `mke2fs` formatting. It is invoked by `mke2fs.c` via `mk_hugefiles()` when profile option `make_hugefiles` is enabled.

Core behavior:
- Reads hugefile settings from the active `mke2fs.conf` fs type stack:
  - `make_hugefiles`
  - `hugefiles_uid`
  - `hugefiles_gid`
  - `hugefiles_umask`
  - `num_hugefiles`
  - `hugefiles_slack`
  - `hugefiles_size`
  - `hugefiles_align`
  - `hugefiles_align_disk`
  - `hugefiles_dir`
  - `hugefiles_name`
  - `hugefiles_digits`
  - `zero_hugefiles`
- Requires extents; returns `EXT2_ET_EXTENT_NOT_SUPPORTED` if the target filesystem lacks the extents feature.
- Creates the configured directory path inside the new filesystem.
- Allocates contiguous free ranges directly from the block bitmap and inserts initialized extents manually.
- Optionally zeroes allocated physical blocks to avoid exposing stale data.
- Calculates extent tree overhead and directory-entry slack before choosing the starting block.
- Sets `large_file` if created file size requires it.

Key functions:
- `get_partition_start()` reads `/sys/dev/block/<major>:<minor>/start` on Linux for disk-relative alignment.
- `create_directory()` creates each missing path component and applies configured uid/gid.
- `mk_hugefile()` creates one regular inode, allocates extents, updates block/inode accounting, sets size, and links it into the target directory.
- `calc_overhead()` estimates extent index block overhead for large extent counts.
- `get_start_block()` skips configured free-space slack before allocation.
- `round_up_align()` aligns blocks, optionally relative to partition offset.
- `mk_hugefiles()` orchestrates profile parsing, sizing, alignment, and file loop.

Important dependencies:
- `mke2fs.h`: imports `program_name`, `quiet`, `verbose`, `zero_hugefile`, `fs_types`, and profile helper functions from `mke2fs.c`.
- libext2fs extent, inode, bitmap, and zeroing APIs.
- blkid/sysfs only for device-offset alignment support.

Research notes:
- The implementation intentionally avoids `ext2fs_fallocate()` because the goal is a contiguous physical layout with extent tree blocks near the start of the filesystem.
- If discard/prezero handling in `mke2fs.c` proves blocks are zeroed, it can set global `zero_hugefile = 0`, and this file respects that.
- `num_blocks == 0` means use available space rather than a fixed per-file size; the code derives file count/size depending on which profile values are present.
