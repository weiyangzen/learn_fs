# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_update.c

## Role
Tests UBI volume update and atomic LEB change operations.

## Main Behavior
- Defines varied write chunk sequences around min I/O size, page size, and LEB size boundaries.
- For each alignment and volume type, creates a volume and runs full-volume update tests.
- For dynamic volumes, additionally runs atomic LEB change tests on LEB 0.
- Writes chunks containing mixed random data and `0xFF` tails, then reads back and compares the exact data.

## Interfaces And Dependencies
- Uses `ubi_update_start`, `ubi_leb_change_start`, `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info`.
- Includes both `libubi.h` and kernel `mtd/ubi-user.h`.
- Uses randomized data via `seed_random_generator`.

## Notes
- Deliberately passes the original sequence length to `write()` even when the final chunk is truncated; expects UBI to accept only the remaining announced update bytes.
- Static volumes are read with a request larger than data size to confirm static-volume EOF behavior.
