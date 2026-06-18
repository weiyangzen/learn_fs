# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format_utils.h

Small formatter utility header.

Contents:
- Includes `f2fs_fs.h`.
- Declares external global configuration `struct f2fs_configuration c`.
- Declares formatter utility functions:
  - `f2fs_trim_device(int, uint64_t)`
  - `f2fs_trim_devices(void)`
  - `f2fs_format_device(void)`

Notes:
- `f2fs_trim_device(int, uint64_t)` is declared here but this file group only contains `f2fs_trim_devices()` and an internal `trim_device(int)` implementation in `f2fs_format_utils.c`; the public declaration may be implemented elsewhere or be stale.
- Used by `f2fs_format_main.c` / `f2fs_format.c` to connect command-line flow with formatting and trim helpers.
