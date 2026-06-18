# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/main.c

## Purpose
Module entry point and global config/capability definition for FSAL_PROXY_V4.

## Important APIs, Types, and Functions
Defines global `PROXY_V4`, config items in `proxyv4_params`, config block `proxy_param_v4`, `proxyv4_init_config`, module initializer `proxyv4_init`, and finalizer `proxyv4_unload`.

## Control Flow
Module init registers `PROXY_V4`, installs `init_config` and `create_export`, and initializes handle ops. Config loading applies module parameters and displays fsinfo. Unload unregisters the FSAL.

## State and Persistence Behavior
Owns process-global FSAL module state and advertised capabilities. No persistence; export-specific RPC and handle-map state is created elsewhere.

## Dependencies and Integration Points
Depends on FSAL registration/config APIs and `proxyv4_fsal_methods.h`. Connects `handle.c` ops and `export.c` export creation to the FSAL loader.

## Risks
The module block is `CONFIG_UNIQUE`. Capabilities advertise named attributes and ACL allow support, but `xattrs.c` returns not supported. Export config later validates max IO sizes against RPC buffers.

## Test Signals
Successful registration as `PROXY_V4`, config parse/display, initialized object ops, export creation, and clean unregister.
