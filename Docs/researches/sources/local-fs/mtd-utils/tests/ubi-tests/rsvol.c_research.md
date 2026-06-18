# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/rsvol.c

## Role
UBI volume resize test for dynamic and static volumes.

## Main Behavior
- Creates volumes, shrinks/grows them, and validates metadata with `check_volume`.
- Tests resize to exact LEB size, larger size, and one byte below a LEB multiple.
- For aligned volumes, shrinks by one LEB, writes data, resizes to data bytes, grows to available LEBs, then verifies data preservation.
- Runs across many alignment values and both volume types.

## Interfaces And Dependencies
- Uses `ubi_rsvol`, `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info`, `ubi_get_vol_info1`, `ubi_update_start`.
- Uses direct volume node I/O for data write/read.

## Notes
- Uses VLAs sized by `vol_info->rsvd_bytes`.
- The file comment has a typo, “Tes UBI volume re-size.”
