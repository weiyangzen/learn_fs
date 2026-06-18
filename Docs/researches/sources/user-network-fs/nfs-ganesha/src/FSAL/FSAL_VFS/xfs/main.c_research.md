# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/main.c

## Purpose

This is the FSAL_XFS module entry point. It declares static module capabilities, parses XFS FSAL configuration, probes OFD lock support, registers the FSAL, and initializes object operation vectors. The source was read as a complete 226-line file.

## Important APIs, Types, and Functions

Key symbols are `XFS_SUPPORTED_ATTRIBUTES`, `myname`, static `struct vfs_fsal_module XFS`, `xfs_params`, `xfs_param`, `init_config`, `xfs_init`, and `xfs_unload`. Configurable parameters include link/symlink support, `cansettime`, `maxread`, `maxwrite`, `umask`, `auth_xdev_export`, and `only_one_user`.

## Control Flow

Module load calls `xfs_init`, which registers FSAL name `XFS`, installs module ops (`vfs_create_export`, `vfs_update_export`, `init_config`), and initializes VFS handle ops. Configuration loading optionally creates a temporary file and uses `F_OFD_GETLK` to decide lock support, then loads `xfs_param` into the module and displays final fsinfo. Module unload unregisters the FSAL.

## State and Persistence Behavior

Runtime state is held in the static `XFS` module object: fsinfo capabilities, object ops, and `only_one_user`. The temporary OFD-lock test file is created under `/tmp` and unlinked immediately. No durable FSAL state is written.

## Dependencies and Integration Points

It integrates with FSAL registration, config parsing, VFS export/update functions, and `vfs_handle_ops_init`. Capabilities are consumed by upper NFS protocol code and export creation.

## Risks and Edge Cases

`CONFIG_UNIQUE` prevents multiple XFS module config blocks. OFD-lock probing depends on kernel headers/runtime and silently disables lock support when unavailable. ACL support depends on compile-time `ENABLE_VFS_ACL`.

## Test Signals

Load/unload the module, parse each config item, verify fsinfo values, run with and without OFD lock support, validate `only_one_user` credential behavior through VFS helpers, and run ACL-enabled and ACL-disabled builds.
