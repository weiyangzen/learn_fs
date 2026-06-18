# File Research: sources/teaching/minix/minix/fs/mfs/link.c

`link.c` implements hard links, unlink/rmdir, symbolic-link reads, rename, truncation, hole punching/free-space release, and helper zeroing for partial zones. It is one of the main directory mutation files and relies on `advance`, `search_dir`, `get_inode`, `put_inode`, `truncate_inode`, and `write_map`.

`fs_link` rejects directory hard links, checks `LINK_MAX`, verifies the destination name does not already exist, inserts a new directory entry, and increments the target link count. `fs_unlink` handles both unlink and rmdir entry points, rejecting mountpoints and read-only filesystems, dispatching to `unlink_file` or `remove_dir`. `remove_dir` verifies emptiness through `search_dir(..., IS_EMPTY)`, rejects the root inode, unlinks the directory entry, then removes `.` and `..`.

`fs_rdlink` reads symlink contents from the first mapped block and copies up to the inode size. `fs_rename` handles cross-directory and same-directory rename, mountpoint rejection, ancestor checks for directory moves, replacement of existing targets, insertion/deletion ordering, and `..` updates plus parent link-count maintenance for moved directories.

`fs_trunc` dispatches to full truncation or free-space punching. `truncate_inode` rejects special files, enforces `s_max_size`, frees removed zones, clears the gap when extending, updates size and times, and marks the inode dirty. `freesp_inode` zeroes partial zones and calls `write_map(..., WMAP_FREE)` for fully freed zones, allowing indirect blocks to be reclaimed. `zerozone_half` and `zerozone_range` implement partial-zone zero filling through `get_block_map`.
