<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c

## Purpose

This file defines the NULLFS module object, static filesystem capability defaults, module initialization, module unload, and minimal module configuration behavior.

## Important APIs, Types, and Functions

- `static const char myname[] = "NULL"`: module registration name and library naming anchor.
- Global `struct null_fsal_module NULLFS`: contains `struct fsal_module module` and the NULLFS object ops vector.
- Static `fs_info`: advertises broad capabilities such as large file size, symlink/link/lock support, named attributes, unique handles, ACL support, all attributes, max I/O size, and parent expiry behavior.
- `init_config`: logs filesystem info and supported attributes; no tunables are applied.
- `MODULE_INIT nullfs_init`: registers the FSAL, installs create/update/init module ops, and initializes handle ops.
- `MODULE_FINI nullfs_unload`: unregisters the FSAL.

## Control Flow

On module load, `nullfs_init` calls `register_fsal`, returns early on failure, assigns module operation callbacks, and initializes `NULLFS.handle_ops`. On configuration init, `init_config` only logs. On unload, `nullfs_unload` calls `unregister_fsal` and reports failure to stderr.

## State and Persistence Behavior

The global `NULLFS` module structure persists for the process lifetime while loaded. Runtime exports and handles are managed by other files; this file only seeds default module-level state and operation vectors.

## Dependencies and Integration Points

This file integrates with the FSAL module registry (`register_fsal`, `unregister_fsal`), common FSAL init headers, and methods declared in `nullfs_methods.h`. It uses `FSAL_ID_NO_PNFS`, so NULLFS does not advertise pNFS identity here.

## Risks and Edge Cases

- Static `fs_info` may overstate actual lower-FSAL capabilities; export operations in `export.c` delegate capability queries to the lower FSAL, which should be preferred at runtime.
- A registration failure only prints to stderr and leaves the module unregistered.
- No module tunables means any stack-specific behavior must live in export config.

## Test Signals

Tests should verify module load/unload, registry name `NULL`, exported module ops being non-NULL after initialization, and that `init_config` succeeds without configuration parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/main.c -->
