# File Research: sources/os/linux/linux/fs/udf/udftime.c

Purpose: conversion between UDF disk timestamps and Linux `timespec64`.

Key behavior:
- `udf_disk_stamp_to_time()` decodes UDF timestamp fields, handles type 1 timezone offsets, treats unspecified offset `-2047` as zero, computes Unix seconds via `mktime64()`, applies timezone offset, and sanitizes sub-second fields.
- `udf_time_to_disk_stamp()` writes current timezone type/offset, converts seconds to local timestamp fields, and decomposes nanoseconds into centiseconds, hundreds of microseconds, and microseconds.

Integration:
- Used by `super.c` for volume recording/LVID timestamps and by inode read/write code elsewhere in UDF.

Risks and invariants:
- Leap seconds are intentionally ignored.
- Bogus sub-second fields are clamped to zero on read.
- Timezone uses `sys_tz.tz_minuteswest` when writing disk stamps.
