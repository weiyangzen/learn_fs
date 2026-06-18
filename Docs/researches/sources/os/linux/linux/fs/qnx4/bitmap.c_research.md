# File Research: sources/os/linux/linux/fs/qnx4/bitmap.c

## Role

Implements free-block counting for QNX4 statfs support.

## Key Function

- `qnx4_count_free_blocks()`:
  - locates the `.bitmap` inode saved in `qnx4_sb(sb)->BitMap`;
  - reads bitmap blocks sequentially;
  - counts zero bits as free blocks using `memweight()`;
  - stops on read error and logs an I/O error.

## Research Notes

The driver is read-only, so bitmap handling is limited to counting free space for `statfs`.
