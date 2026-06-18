# File Research: sources/os/linux/linux/fs/fat/fat_test.c

## Purpose
KUnit tests for FAT helper behavior, focused on short-name checksum and FAT timestamp conversions/truncation.

## Test Coverage
- `fat_checksum_test()` validates checksum values for representative 8.3 names.
- Parameterized `fat_time_fat2unix_test()` validates FAT date/time/centisecond to Unix `timespec64`.
- Parameterized `fat_time_unix2fat_test()` validates Unix to FAT conversion.
- `fat_time_unix2fat_clamp_test()` validates clamping before 1980 and after 2107, including timezone shifts.
- `fat_time_unix2fat_no_csec_test()` checks conversion when the centisecond output pointer is `NULL`.
- `fat_truncate_atime_test()` validates FAT atime truncation to local-day granularity.

## Important Cases
The tests include earliest and latest FAT dates, leap years including 2000 and non-leap 2100, odd-second VFAT centisecond behavior, 10 ms centisecond precision, and timezone offsets that cross date boundaries.

## Dependencies
Exercises exported helpers from `misc.c` and inline `fat_checksum()` from `fat.h`. Uses a zeroed fake `msdos_sb_info` with only timestamp offset fields populated.

## Research Notes
The test file documents the intended FAT timestamp range and timezone semantics. It does not cover directory, cluster, allocation, or mount behavior.
