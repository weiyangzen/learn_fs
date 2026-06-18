# File Research: sources/teaching/pintos/src/filesys/directory.c

## Purpose
Implements Pintos directory handling over inode-backed fixed-size directory files. This is a simple root-directory-oriented layer used by `filesys.c` for name lookup, create, remove, and listing.

## Main Data Structures
- `struct dir`
  - Holds the backing `struct inode *`.
  - Tracks sequential read position in `pos`.
- `struct dir_entry`
  - Stores `inode_sector`, fixed-size `name[NAME_MAX + 1]`, and `in_use`.
  - Directory storage is a linear array of these entries inside the directory inode.

## Key Functions
- `dir_create(sector, entry_cnt)`
  - Creates an inode sized to hold `entry_cnt` directory entries.
- `dir_open(inode)`
  - Takes ownership of an inode and wraps it in `struct dir`.
  - Closes the inode on allocation failure or null inode.
- `dir_open_root()`
  - Opens `ROOT_DIR_SECTOR` through `inode_open()`.
- `dir_reopen(dir)`
  - Reopens the same backing inode.
- `dir_close(dir)`
  - Closes the backing inode and frees the wrapper.
- `dir_get_inode(dir)`
  - Exposes the backing inode.
- `lookup(dir, name, ep, ofsp)`
  - Private linear scan over directory entries.
  - Returns entry contents and/or byte offset when requested.
- `dir_lookup(dir, name, inode)`
  - Finds a named entry and opens its inode.
- `dir_add(dir, name, inode_sector)`
  - Rejects empty names and names longer than `NAME_MAX`.
  - Rejects duplicate live entries.
  - Reuses the first free slot or attempts to append at EOF.
- `dir_remove(dir, name)`
  - Clears the directory entry, opens the inode, and marks it removed.
- `dir_readdir(dir, name)`
  - Sequentially returns live entry names, skipping free slots.

## Important Behavior
- Directory lookup is flat; this file does not parse paths or nested directories.
- There are no `"."` or `".."` entries.
- `dir_add()` comments mention appending at EOF, but the current inode layer does not grow files. A directory created with `entry_cnt` entries has a hard capacity unless inode growth is implemented.
- Removal first clears the directory entry, then calls `inode_remove()`. Actual block release happens later in `inode_close()` when the last opener closes the inode.
- No internal locking is present; callers must rely on higher-level synchronization if concurrent access is introduced.

## Dependencies
- Uses `filesys/filesys.h` for `ROOT_DIR_SECTOR`.
- Uses `filesys/inode.h` for all backing storage reads/writes and inode lifecycle.
- Uses `threads/malloc.h` for allocation.

## Research Notes
- Name length is coupled to `NAME_MAX` in `directory.h`.
- Directory entries are stored as ordinary inode data; there is no special block layout beyond fixed-size serialized `struct dir_entry` records.
