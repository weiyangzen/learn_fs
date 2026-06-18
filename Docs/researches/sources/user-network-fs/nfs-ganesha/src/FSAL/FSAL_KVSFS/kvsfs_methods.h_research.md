# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_methods.h

Purpose: Declares the KVSFS FSAL private structures and cross-file method prototypes used by module, export, handle, pNFS, xattr, locking, and I/O implementations.

Important APIs and types: Key structs include `kvsfs_fsal_module`, `kvsfs_fsal_export`, `kvsfs_exp_pnfs_parameter`, `kvsfs_pnfs_ds_parameter`, `kvsfs_fd`, `kvsfs_state_fd`, and `kvsfs_fsal_obj_handle`. It declares `kvsfs_handle_ops_init()`, export lookup/reconstruction helpers, `kvsfs_alloc_handle()`, all open/read/write/commit/close helpers, share/lock helpers, and extended attribute operations.

Control flow: This header is the contract that lets `kvsfs_main.c` initialize ops, `kvsfs_handle.c` allocate/reconstruct handles and dispatch operations, export code call path and wire-handle creation, and xattr/pNFS code register into the same object ops vector. It also defines `KVSFS_NB_DS` and pNFS export parameter layout used by MDS device encoding.

State and persistence: The header documents state ownership. `kvsfs_fsal_export` owns root inode, KVSNS config path, pNFS enable flags, and DS parameters. `kvsfs_fsal_obj_handle` owns an allocated variable-size `kvsfs_file_handle` pointer plus either file state or symlink content. `kvsfs_state_fd` embeds `state_t` first, matching Ganesha's default state-freeing convention.

Dependencies and integration: Depends on FSAL types, Ganesha list/fd/share/state primitives, KVSNS inode/open/credential types, and pNFS sockaddr definitions. It is included by most KVSFS implementation files.

Risks: The comment notes `kvsfs_pnfs_ds_parameter` needs refactoring because port is separate from `sockaddr_in`; byte order and config parsing errors are likely here. Fixed `KVSFS_NB_DS = 4` limits DS scaling. The object handle stores both opaque handle pointer and inode field in the file union, so duplication must stay coherent. Xattr and lock prototypes imply support that module static info may not advertise accurately.

Test signals: Compile all KVSFS variants with pNFS on/off, verify struct layout assumptions for state embedding and handle allocation, exercise wire-handle sizing, and check static capability flags against the operations declared here.
