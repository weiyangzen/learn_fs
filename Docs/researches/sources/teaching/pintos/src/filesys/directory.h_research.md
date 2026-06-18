# File Research: sources/teaching/pintos/src/filesys/directory.h

## Purpose
Public interface for Pintos directory operations.

## Exposed API
- Directory lifecycle:
  - `dir_create`
  - `dir_open`
  - `dir_open_root`
  - `dir_reopen`
  - `dir_close`
  - `dir_get_inode`
- Directory operations:
  - `dir_lookup`
  - `dir_add`
  - `dir_remove`
  - `dir_readdir`

## Key Constants
- `NAME_MAX` is `14`, matching the traditional UNIX component-name limit used by this teaching implementation.

## Dependencies
- Includes `<stdbool.h>`, `<stddef.h>`, and `devices/block.h`.
- Forward declares `struct inode`.

## Research Notes
- The comment anticipates future directory support where full path names may exceed `NAME_MAX`, but this interface only supports one component at a time.
- `struct dir` is intentionally opaque to callers.
