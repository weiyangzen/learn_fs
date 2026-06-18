# File Research: sources/local-fs/xfsdump/common/timeutil.h

## Role

This header declares helper functions for formatting `time32_t` values.

## API

- `ctime32()`
- `ctime32_r()`
- `ctimennl()`

The API exists to keep xfsdump's on-disk or compatibility time type separate from platform `time_t` at call sites.
