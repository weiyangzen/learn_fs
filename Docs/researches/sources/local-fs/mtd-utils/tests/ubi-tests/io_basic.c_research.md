# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_basic.c

## Role
Basic UBI volume I/O test for dynamic and static volumes.

## Main Behavior
- Creates a volume using all available bytes, checks new contents are `0xFF`, writes an `0xA5` pattern through volume update, verifies it, then removes the volume.
- Repeats the same pattern across many alignment values derived from `ALIGNMENTS(dev_info.leb_size)`.
- Tests both `UBI_DYNAMIC_VOLUME` and `UBI_STATIC_VOLUME`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Relies on helper macros/functions: `initial_check`, `check_vol_patt`, `update_vol_patt`, `failed`.
- Builds volume node names from `UBI_VOLUME_PATTERN`.

## Notes
- Alignment is rounded down to a multiple of `dev_info.min_io_size`, with zero corrected to `min_io_size`.
- The test assumes the passed UBI device has enough free eraseblocks and no conflicting volumes.
