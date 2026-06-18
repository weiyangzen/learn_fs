# File Research: sources/local-fs/xfsdump/common/path.h

## Role

This header declares pathname utility functions.

## API

- `path_reltoabs()`
- `path_normalize()`
- `path_diff()`
- `path_beginswith()`

The functions return allocated normalized paths where applicable and are used by higher-level command/path handling.
