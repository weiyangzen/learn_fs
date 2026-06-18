# File Research: sources/os/linux/linux/fs/bfs/Kconfig

## Purpose
Kernel configuration entry for SCO UnixWare BFS filesystem support.

## Configuration
- Symbol: `BFS_FS`
- Type: tristate
- Prompt: `BFS file system support`
- Depends on: `BLOCK`
- Selects: `BUFFER_HEAD`

## Help Text
Describes BFS as the Boot File System used by SCO UnixWare for bootloader access to the kernel and important files, usually mounted at `/stand` on a UnixWare `STAND` slice. Notes that Linux can read/write these files and points to `Documentation/filesystems/bfs.rst`.

## Research Notes
The config allows BFS as built-in or module `bfs`, but warns root filesystem support cannot be modular.
