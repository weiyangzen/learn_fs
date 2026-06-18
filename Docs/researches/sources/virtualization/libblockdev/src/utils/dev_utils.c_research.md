# File Research: sources/virtualization/libblockdev/src/utils/dev_utils.c

This file implements block-device resolution and udev symlink discovery.

Functions:
- `bd_utils_dev_utils_error_quark()` returns the device-utils error domain.
- `_is_block_device()` uses `stat()` and `S_ISBLK` to verify a path is a block device.
- `bd_utils_resolve_device()` normalizes a device spec to `/dev/...`, resolves one symlink level, and verifies the result is a block device.
- `bd_utils_get_device_symlinks()` resolves the device, looks it up in udev’s block subsystem, and returns all devlinks known to udev.

Resolution details:
- If `dev_spec` lacks `/dev/`, `/dev/` is prepended.
- `g_file_read_link()` returning `G_FILE_ERROR_INVAL` is treated as “not a symlink”.
- Relative symlinks beginning with `../` are converted to `/dev/<target after ../>`.
- Other symlink targets are converted to `/dev/<target>`.
- All returned device paths are verified as block devices.

Research relevance:
- `bd_swap_swapstatus()` depends on this helper for `/dev/mapper/` and `/dev/md/` names.
- Only a single symlink read is performed; nested symlink behavior depends on the immediate `/dev` layout.
- udev lookup uses sysname from the resolved `/dev/<name>` path.
