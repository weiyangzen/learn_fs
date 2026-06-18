# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_MEM/mem_main.c

## Purpose
`mem_main.c` is the module entry/exit and global configuration file for FSAL_MEM. It defines the MEM `fsal_module`, default static filesystem capabilities, module-level config block, async worker package lifecycle, and `MODULE_INIT`/`MODULE_FINI` hooks.

## Important APIs, Types, And Functions
The global `struct mem_fsal_module MEM` initializes FSAL capabilities such as POSIX attributes, unique handles, link and symlink support, readdir plus support, no lock support, max read/write sizes, and time support. `mem_items` exposes `Inode_Size`, `Up_Test_Interval`, `Async_Threads`, and `Whence_is_name`. `mem_block` registers those settings under the `MEM` config block. `mem_async_fridge` is the async I/O worker pool used by `mem_handle.c`.

`mem_async_pkginit()` creates a `fridgethr` worker pool named `MEM_ASYNC_fridge` when `Async_Threads` is nonzero. `mem_async_pkgshutdown()` stops, cancels on timeout, destroys, and clears the async fridge. `mem_init_config()` loads module config, starts the upcall test package, starts the async package, mirrors `whence_is_name` into fsinfo, and logs capabilities. `init()` registers the FSAL and wires module ops and handle ops. `finish()` shuts down upcalls, async workers, and unregisters the FSAL.

## Control Flow
On load, `init()` calls `register_fsal()`, assigns `create_export`, `update_export`, and `init_config`, initializes the module export list, seeds `MEM.next_inode`, and calls `mem_handle_ops_init()`. During configuration, `mem_init_config()` parses `MEM`, then starts optional background packages. On unload, `finish()` tears down background packages before unregistering the module; unregister failure is fatal and aborts.

## State And Persistence
Module config is held in the global `MEM` object for the process lifetime. `MEM.mem_exports` tracks live exports; `mem_up.c` iterates it for test upcalls. `mem_async_fridge` is process-global and shared by all MEM exports. No state persists across module reload or process restart.

## Dependencies And Integration Points
This file integrates with Ganesha module registration, config parsing, FSAL private helpers, fridgethr workers, MEM handle/export/upcall functions, and fsinfo display. `Inode_Size` directly controls allocation behavior in `mem_handle.c`; `Up_Test_Interval` controls `mem_up.c`; `Async_Threads` controls async read/write completions.

## Risks
Async initialization succeeds as a no-op when thread count is zero; callers must tolerate inline-only I/O. If `mem_up_pkginit()` succeeds but async init fails, the code returns failure without explicitly shutting down the upcall package in that path. Configuration allows very large per-file `Inode_Size` up to 0x200000, so tests that create many files can consume memory quickly.

## Test Signals
Exercise module load/config/unload with zero and nonzero `Async_Threads` and `Up_Test_Interval`, invalid config values, repeated init/shutdown, and export creation after config. Check that `whence_is_name` appears in fsinfo, async fridge is destroyed on unload, and no worker threads survive shutdown timeout paths.
