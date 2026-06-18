# File Research: sources/local-fs/xfsprogs/db/init.c

## Purpose
Contains xfs_db process initialization and `main`: option parsing, libxfs setup, superblock loading, mount creation, command initialization, command-line execution, interactive input loop, and shutdown.

## Main Interfaces
- Defines global state `mp`, `x`, `blkbb`, `exitcode`, `expert_mode`, and `cur_agno`.
- Supports startup options for commands (`-c`), image file mode (`-f`), forced non-XFS read (`-F`), inactive/read-only modes (`-i`, `-r`), program name (`-p`), log/realtime devices (`-l`, `-R`), expert mode (`-x`), and version (`-V`).

## Control Flow
`init()` initializes locale, parses options, calls `libxfs_init`, reads the primary superblock uncached without verifier validation, mounts with `LIBXFS_MOUNT_DEBUGGER`, initializes per-AG data when possible, selects the type table variant for CRC/sparse-inode filesystems, pushes the first IO cursor, and registers commands/signals. `main()` executes `-c` commands first; without `-c`, it pushes stdin and loops over `fetchline()`, `breakline()`, `command()`, and cleanup. Shutdown pops temporary IO contexts, unmounts libxfs, destroys devices, and returns `exitcode`.

## Dependencies
Integrates libxfs/libxlog, command registration, input, IO cursor stack, signal handling, output, malloc wrappers, and type table selection.

## Risks And Invariants
- The debugger mount intentionally tolerates damaged filesystems more than normal mount paths.
- `-F` only bypasses the primary magic-number refusal; later mount setup can still fail.
- Buffers held by extra IO stack entries are popped before `libxfs_umount` to avoid cache purge issues.
