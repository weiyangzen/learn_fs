# File Research: sources/local-fs/jfsutils/xpeek/super2.c

Implements an alternate superblock display/edit command, exposed as `s2perblock` in the command dispatcher. It shows a different layout including `s_aim2` and fsck log fields.

Main command:
- `superblock2(void)`: accepts optional `p` or `s`, reads primary/secondary superblock with `ujfs_get_superblk`, calls `display_super2`, and writes back if changed.

Display/edit:
- `display_super2(struct superblock *)`: prints fields similar to `display_super`, but with alternate ordering and additional fields:
  - `s_aim2` PXD,
  - `s_fsckloglen`,
  - `s_fscklog`,
  - shortened flag/state labels,
  - UUID, label, and log UUID for current JFS version.
- Supports modifications for up to 32 fields when `s_version == JFS_VERSION`, otherwise up to 29 fields.
- Parses UUIDs through `uuid_parse`.

Integration points:
- Declared locally and referenced as `extern void superblock2(void)` in `xpeek.c`.
- Help text calls the command `s2perblock`.
- Uses `jfs_byteorder.h`, `jfs_filsys.h`, and `super.h`.

Notable behavior and risks:
- Same raw superblock-editing risks as `super.c`.
- There is an apparent naming mismatch: `xpeek.h` declares `void s2perblock(void);`, but this file implements `superblock2(void)` and `xpeek.c` calls `superblock2`.
- Argument handling shares the same weak “too many arguments” pattern as `super.c`.
