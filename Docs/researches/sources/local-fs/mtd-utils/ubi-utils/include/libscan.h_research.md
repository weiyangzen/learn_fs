# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libscan.h

## Role
Public API for scanning MTD eraseblocks for UBI erase-counter state.

## Main Contents
- Defines special erase-counter/status constants: `NO_EC`, `CORRUPT_EC`, `EB_EMPTY`, `EB_CORRUPTED`, `EB_ALIEN`, `EB_BAD`, and `EC_MAX`.
- Defines `struct ubi_scan_info` with per-eraseblock EC/status array and summary counters.
- Declares `ubi_scan` and `ubi_scan_free`.

## Interfaces And Dependencies
- Depends on `stdint.h`, UBI media constants, and forward-declared `struct mtd_dev_info`.
- Implemented by `libscan.c`.

## Notes
- `vid_hdr_offs` and `data_offs` are set to `-1` when undefined.
- Used heavily by `ubiformat.c`.
