# File Research: sources/teaching/pintos/src/filesys/filesys.c

## Purpose
Top-level Pintos file-system module. It initializes the file-system device, free map, and inode layer, and exposes simple root-directory file create/open/remove operations.

## Global State
- `struct block *fs_device`
  - The block device selected by `BLOCK_FILESYS`.
  - Shared by inode and free-map code.

## Key Functions
- `filesys_init(format)`
  - Finds the file-system block device.
  - Initializes inode and free-map modules.
  - Optionally formats the file system.
  - Opens the persisted free-map file.
- `filesys_done()`
  - Closes the free-map file.
- `filesys_create(name, initial_size)`
  - Opens the root directory.
  - Allocates one sector for the new inode.
  - Creates the inode with requested initial size.
  - Adds the name to the root directory.
- `filesys_open(name)`
  - Looks up a name in the root directory and wraps the inode in `struct file`.
- `filesys_remove(name)`
  - Removes a root-directory entry.
- `do_format()`
  - Creates a new free map.
  - Creates root directory inode at `ROOT_DIR_SECTOR` with 16 entries.
  - Closes the temporary free-map file.

## Important Behavior
- Only flat root-directory file names are supported; no path traversal appears here.
- System inode sectors are fixed:
  - free-map inode at sector `0`
  - root-directory inode at sector `1`
- `filesys_create()` releases the allocated inode sector if the overall operation fails after allocation. If `inode_create()` succeeds but `dir_add()` fails, the inode’s data sectors are not explicitly released here; cleanup is incomplete in that failure path.
- Formatting creates a root directory with capacity for 16 entries. Since inode growth is absent, this is effectively the root directory capacity.

## Dependencies
- `devices/block` role lookup through included headers.
- `filesys/free-map.h` for allocation and free-map lifecycle.
- `filesys/inode.h` for inode initialization and creation.
- `filesys/directory.h` for root-directory operations.
- `filesys/file.h` for returning open files.

## Research Notes
- This file is the public bridge between syscall/user-facing file operations and the lower inode/directory/free-map layers.
