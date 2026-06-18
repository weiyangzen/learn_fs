# File Research: sources/local-fs/mtd-utils/ubi-utils/ubidetach.c

## Role
CLI tool to detach MTD devices from UBI or remove a UBI device by number.

## Main Behavior
- Parses UBI device number, MTD node path, MTD number, and control device path.
- Defaults control node to `/dev/ubi_ctrl`.
- Opens libubi, verifies control-device support, and performs exactly one detach/remove mode:
  - remove by UBI device number,
  - detach by MTD node,
  - detach by MTD number.

## Interfaces And Dependencies
- Uses `ubi_remove_dev`, `ubi_detach`, `ubi_detach_mtd`, and `ubi_get_info`.
- Uses `common.h` parsing and diagnostic helpers.

## Notes
- Rejects ambiguous requests that specify both UBI device and MTD target, or both MTD number and MTD node.
- Error text says “MTD detach/detach feature,” likely intended as attach/detach.
