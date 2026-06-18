# File Research: sources/local-fs/xfsdump/common/openutil.h

## Role

This header declares utility functions for constructing pathnames and opening or creating support files.

## API

- `open_pathalloc()`
- `open_trwdb()` / `open_trwp()`
- `open_rwdb()` / `open_rwp()`
- `open_erwdb()` / `open_erwp()`
- `mkdir_tp()`

The API is centered on read-write temporary or housekeeping files with optional PID-suffixed names.
