# File Research: sources/teaching/pintos/src/filesys/free-map.h

## Purpose
Public interface for free-sector bitmap management.

## Exposed API
- Lifecycle:
  - `free_map_init`
  - `free_map_read`
  - `free_map_create`
  - `free_map_open`
  - `free_map_close`
- Allocation:
  - `free_map_allocate`
  - `free_map_release`

## Dependencies
- Includes `<stdbool.h>`, `<stddef.h>`, and `devices/block.h`.

## Research Notes
- `free_map_read()` is declared here but is not implemented in `free-map.c`; the implementation uses `free_map_open()` to open and read the bitmap.
- Allocation and release operate in units of block sectors.
