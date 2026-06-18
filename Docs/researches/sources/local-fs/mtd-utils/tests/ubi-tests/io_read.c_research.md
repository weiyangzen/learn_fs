# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/io_read.c

## Role
Read-boundary and static-volume read semantics test for UBI volumes.

## Main Behavior
- Verifies a newly created static volume has `data_bytes == 0` and reads as EOF before update.
- Writes 10 bytes to a static volume and checks reads return exactly the data length.
- Creates dynamic/static volumes with many alignments, fills them with byte patterns, then tests reads across many offsets and lengths.
- Confirms resulting file offset after each read matches bytes actually read.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_update_start`, `ubi_get_vol_info`, `ubi_get_dev_info`.
- Uses `lseek`, `read`, `write`, and direct volume device nodes.
- Uses `ALIGNMENTS`, `PAGE_SIZE`, `MIN_AVAIL_EBS`, and test error helpers.

## Notes
- `PROGRAM_NAME` is set to `"io_basic"` even though the file is `io_read.c`, so diagnostic labels may be misleading.
- Uses stack VLAs sized by test length and volume size.
