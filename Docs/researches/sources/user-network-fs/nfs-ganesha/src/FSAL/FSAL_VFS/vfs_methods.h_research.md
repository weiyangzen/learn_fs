# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs_methods.h

## Purpose

This header is the central internal contract for FSAL_VFS. It defines VFS module/export/object structures, inline helpers, and prototypes for export, handle, state, I/O, xattr, credential, and filesystem-handle operations. The source was read as a complete 402-line file.

## Important APIs, Types, and Functions

Core types are `struct vfs_fsal_module`, `struct vfs_fsal_export`, `struct vfs_subfsal_obj_ops`, `struct vfs_fd`, `struct vfs_state_fd`, `struct vfs_fsal_obj_handle`, and `struct closefd`. Conversion macros include `EXPORT_VFS_FROM_FSAL` and `OBJ_VFS_FROM_FSAL`. Important APIs include `vfs_create_export`, `vfs_update_export`, `vfs_lookup_path`, `vfs_create_handle`, `vfs_fd_to_handle`, `vfs_name_to_handle`, `vfs_open_by_handle`, `vfs_check_handle`, `vfs_get_root_handle`, `vfs_fsal_open`, `alloc_handle`, `free_vfs_fsal_obj_handle`, `vfs_open2/read2/write2/setattr2/close2`, xattr operations, HSM and FS_LOCATIONS helpers, and `find_fd`.

## Control Flow

The header does not execute by itself, but it shapes runtime dispatch. Module registration installs FSAL ops; export methods create VFS handles; handle methods use the syscall helpers to convert file descriptors, path names, wire handles, and root filesystem state into FSAL object handles; I/O/state paths use `vfs_fd` or `vfs_state_fd`; xattr and credential helpers are called by object methods.

## State and Persistence Behavior

The state model is in-memory. `vfs_fsal_export` stores FSID and async HSM options. `vfs_fsal_obj_handle` stores the FSAL object, device id, handle bytes, sub-FSAL ops, upcall vector, and a union for file descriptors/share state, symlink contents, or unopenable socket/device names. Persistence on disk is delegated to kernel filesystems.

## Dependencies and Integration Points

Includes connect this header to `fsal_handle_syscalls.h`, `fsal_api.h`, FSAL commonlib/localfs, and access checks. It is consumed by generic VFS files, the XFS specialization, xattr code, state handling, and export creation.

## Risks and Edge Cases

`root_fd` stores an integer fd through `fs->private_data`, so ownership and lifetime must match filesystem claim/unclaim rules. `vfs_unopenable_type` must stay aligned with handle allocation for sockets and devices. Credential helpers branch on `only_one_user`; missed restore calls can leak effective credentials.

## Test Signals

Compile coverage across all VFS sub-FSALs is essential. Behavioral tests should exercise file, directory, symlink, socket/device handles, root-handle extraction, multi-state open/read/write/close, credential switching, xattr dispatch, and stale handle validation.
