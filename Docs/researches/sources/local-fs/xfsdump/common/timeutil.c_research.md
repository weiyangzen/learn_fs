# File Research: sources/local-fs/xfsdump/common/timeutil.c

## Role

This file provides `time32_t` wrappers around C library time formatting routines.

## Functions

- `ctime32()` casts a `time32_t` to `time_t` and calls `ctime()`.
- `ctime32_r()` casts a `time32_t` to `time_t` and calls `ctime_r()`.
- `ctimennl()` formats time with `ctime32()` and removes the trailing newline from the returned static buffer.

## Assumptions

The conversion assumes the current platform `time_t` can represent the supplied 32-bit time value.
