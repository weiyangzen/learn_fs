# File Research: sources/teaching/pintos/src/filesys/filesys.h

## Purpose
Public top-level file-system interface and shared file-system constants.

## Key Constants
- `FREE_MAP_SECTOR 0`
  - Inode sector for the free-map file.
- `ROOT_DIR_SECTOR 1`
  - Inode sector for the root-directory file.

## Exposed State
- `extern struct block *fs_device`
  - Shared global block device pointer used by inode and free-map implementations.

## Exposed API
- `filesys_init`
- `filesys_done`
- `filesys_create`
- `filesys_open`
- `filesys_remove`

## Dependencies
- Includes `<stdbool.h>` and `filesys/off_t.h`.

## Research Notes
- The API exposes only flat file operations by name; directory traversal is not part of this interface.
