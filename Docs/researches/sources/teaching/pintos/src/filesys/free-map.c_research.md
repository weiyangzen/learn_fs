# File Research: sources/teaching/pintos/src/filesys/free-map.c

## Purpose
Manages sector allocation using a bitmap persisted as a special file in the Pintos file system.

## Global State
- `free_map_file`
  - Open file handle for the on-disk free-map file.
- `free_map`
  - In-memory bitmap with one bit per file-system sector.

## Key Functions
- `free_map_init()`
  - Creates a bitmap sized to `block_size(fs_device)`.
  - Marks `FREE_MAP_SECTOR` and `ROOT_DIR_SECTOR` as reserved.
- `free_map_allocate(cnt, sectorp)`
  - Scans for `cnt` consecutive free sectors and flips them allocated.
  - If the free-map file is open, writes the bitmap to disk.
  - Rolls back the allocation if bitmap persistence fails.
- `free_map_release(sector, cnt)`
  - Asserts all target sectors are allocated.
  - Clears them and writes the bitmap to disk.
- `free_map_open()`
  - Opens the free-map file at `FREE_MAP_SECTOR`.
  - Reads the persisted bitmap into memory.
- `free_map_close()`
  - Closes `free_map_file`.
- `free_map_create()`
  - Creates the free-map inode sized to `bitmap_file_size(free_map)`.
  - Opens it and writes the initial bitmap.

## Important Behavior
- Allocation requires contiguous sectors. This matches the simple extent-style inode format.
- During early format, allocations can occur before `free_map_file` exists; persistence is skipped until the file is created.
- `free_map_close()` does not null out `free_map_file`.
- `free_map_release()` always calls `bitmap_write(free_map, free_map_file)`, so callers must not release sectors before the file is available.

## Dependencies
- Uses Pintos `bitmap` helpers.
- Uses `filesys/file.h` and `filesys/inode.h` to store the bitmap as a regular inode-backed file.
- Uses `filesys/filesys.h` for fixed sector constants and `fs_device`.

## Research Notes
- `free-map.h` declares `free_map_read()`, but this implementation file does not define it. The active read operation is `free_map_open()`.
