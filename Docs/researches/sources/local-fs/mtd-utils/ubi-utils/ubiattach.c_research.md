# File Research: sources/local-fs/mtd-utils/ubi-utils/ubiattach.c

## Role
CLI tool to attach an MTD device to UBI.

## Main Behavior
- Parses UBI device number, MTD node path, MTD number, VID header offset, maximum expected bad blocks per 1024 PEBs, and control device path.
- Defaults control node to `/dev/ubi_ctrl`.
- Opens libubi, verifies control-device support, builds `ubi_attach_request`, and calls `ubi_attach`.
- Prints summary of the newly created UBI device.

## Interfaces And Dependencies
- Uses `libubi` and `ubiutils-common`.
- Uses `simple_strtoul`, diagnostics, and version helpers from `common.h`.

## Notes
- Supports old-kernel compatibility where `max_beb_per1024` may be ignored and reported as warning.
- Requires either `--mtdn` or `--dev-path`.
