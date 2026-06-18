# File Research: sources/os/linux/linux-stable/fs/fat/fat_test.c

This file contains KUnit coverage for FAT checksum and timestamp conversion behavior.

Covered behavior:
- `fat_checksum()` is tested against known 8.3 aliases without extension, with a three-letter extension, and with a one-letter extension.
- `fat_time_fat2unix()` and `fat_time_unix2fat()` are tested across FAT date range limits, leap years, UTC offsets, odd seconds, and centisecond precision.
- `fat_time_unix2fat()` clamp behavior is tested below 1980 and above 2107, including timezone offsets that push otherwise-valid UTC values out of FAT range.
- `fat_time_unix2fat()` is also tested with a `NULL` centisecond pointer.
- `fat_truncate_atime()` is tested for FAT’s local-day access-time truncation behavior under UTC and offset timezones.

Important structures:
- `fat_timestamp_testcase` stores bidirectional timestamp conversion cases.
- `fat_unix2fat_clamp_testcase` stores out-of-range conversion clamp cases.
- `fat_truncate_atime_testcase` stores expected local-midnight truncation cases.

Important functions:
- `fat_test_set_time_offset()` builds a minimal fake `msdos_sb_info` with `tz_set` and `time_offset`.
- Parameterized KUnit tests use `KUNIT_ARRAY_PARAM()` for timestamp, clamp, and atime truncation cases.
- `fat_test_suite` registers all test cases under the `fat_test` suite.

Research relevance:
- This file documents expected FAT timestamp semantics, especially the tricky 1980-2107 range, 2-second mtime granularity, 10ms creation-time centiseconds, and local-time access-date truncation.
