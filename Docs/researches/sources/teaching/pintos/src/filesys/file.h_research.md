# File Research: sources/teaching/pintos/src/filesys/file.h

## Purpose
Public open-file interface for Pintos.

## Exposed API
- Lifecycle:
  - `file_open`
  - `file_reopen`
  - `file_close`
  - `file_get_inode`
- I/O:
  - `file_read`
  - `file_read_at`
  - `file_write`
  - `file_write_at`
- Write control:
  - `file_deny_write`
  - `file_allow_write`
- Position and size:
  - `file_seek`
  - `file_tell`
  - `file_length`

## Dependencies
- Includes `filesys/off_t.h`.
- Forward declares `struct inode`.

## Research Notes
- `struct file` is opaque to callers.
- Offset and length types use Pintos-local `off_t`, defined as signed 32-bit.
