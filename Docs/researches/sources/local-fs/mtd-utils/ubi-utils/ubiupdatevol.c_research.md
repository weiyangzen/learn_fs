# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiupdatevol.c

## Purpose
Implements `ubiupdatevol`, the utility for updating or truncating the contents of an existing UBI volume node.

## Main Entry Points
- `parse_opt()` parses truncate mode, explicit input size, input skip offset, help, version, volume node, and image path or stdin marker.
- `truncate_volume()` starts a zero-length UBI update to wipe the volume.
- `ubi_write()` writes a buffer fully to the volume, retrying interrupted writes.
- `update_volume()` validates input size against reserved volume bytes, opens the volume and input, starts a UBI update, and streams data in LEB-sized chunks.
- `main()` validates the node as a UBI volume node, fetches volume info, and dispatches truncate or update mode.

## Control Flow
The command expects a UBI volume node. In truncate mode, it opens the node read/write and calls `ubi_update_start()` with size zero. In update mode, it derives the input byte count from `--size` or from `stat(image) - skip`, checks that the data fits in `vol_info.rsvd_bytes`, opens the volume and input file, optionally seeks past skipped input bytes, starts the update with the final byte count, and copies data until the requested byte count is written.

Stdin input is selected by using `-` as the image path and requires an explicit `--size`; skipping stdin is rejected.

## Dependencies
Uses `libubi` for probing, volume info, and update start. Uses POSIX open/read/write/lseek/stat/close APIs and local `common.h` diagnostics.

## Risks and Notes
`parse_opt()` sets `args.img = argv[optind + 1]` even in truncate mode where the image argument is not required; because the global `args` object is zero-initialized this is usually benign when `optind + 1 == argc`, but it still reads one element past the logical argument list. If `stat()` fails before `err` is set to the function’s return value in `update_volume()`, the error path returns the previous uninitialized/local value rather than a deliberate `-1`. The pointer arithmetic in `ubi_write()` advances a `const void *`, which is a GNU C extension rather than strictly portable C.
