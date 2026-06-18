# File Research: sources/teaching/pintos/src/filesys/inode.h

## Purpose
Public interface for inode lifecycle, I/O, write-denial, and length queries.

## Exposed API
- Lifecycle:
  - `inode_init`
  - `inode_create`
  - `inode_open`
  - `inode_reopen`
  - `inode_get_inumber`
  - `inode_close`
  - `inode_remove`
- I/O:
  - `inode_read_at`
  - `inode_write_at`
- Write control:
  - `inode_deny_write`
  - `inode_allow_write`
- Metadata:
  - `inode_length`

## Dependencies
- Includes `<stdbool.h>`, `filesys/off_t.h`, and `devices/block.h`.
- Forward declares `struct bitmap`, though this header does not expose bitmap-taking functions.

## Research Notes
- `struct inode` is opaque outside `inode.c`.
- All offsets and sizes use Pintos-local `off_t`.
