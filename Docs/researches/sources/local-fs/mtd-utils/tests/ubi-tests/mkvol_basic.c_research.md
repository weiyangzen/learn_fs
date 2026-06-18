# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_basic.c

## Role
Positive tests for basic UBI volume creation, deletion, alignment, and maximum-volume count behavior.

## Main Behavior
- Creates and removes maximum-size dynamic and static volumes.
- Verifies removed volumes no longer appear via `ubi_get_vol_info1`.
- Creates full-size dynamic volumes across many alignment values and validates computed volume properties.
- Creates many one-byte static volumes up to `max_vol_count` or until `ENFILE`.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_vol_info1`, `ubi_get_dev_info`.
- Uses `check_volume` helper to validate volume metadata against request parameters.

## Notes
- Alignment reduces usable LEB size, and the test computes requested bytes from aligned eraseblock size.
- Destructive test: assumes the target UBI device can be filled and emptied.
