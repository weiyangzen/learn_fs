<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c

## Purpose
Implements NFSv3 `MKNOD`, creating special non-regular filesystem objects such as character devices, block devices, sockets, and FIFOs.

## APIs, Types, and Functions
The exported functions are `nfs3_mknod()` and `nfs3_mknod_free()`. It consumes `MKNOD3args`, maps NFSv3 node types to `object_file_type_t`, converts attributes through `nfs3_Sattr_To_FSALattr()`, sets `ATTR_RAWDEV` for device numbers, checks inode quota, uses `fsal_create()`, builds NFSv3 file handles with `nfs3_FSALToFhandle()`, and returns WCC via `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves and validates the parent directory, validates the object name, decodes the requested node type and type-specific attributes, rejects unsupported/bad types, checks quota, applies `squash_setattr()`, supplies a default mode if missing, and creates the object. Success returns a new post-op handle, attributes, and parent WCC. Failure maps FSAL status and returns parent WCC when possible. Persistent filesystem state changes only through `fsal_create()`.

## Dependencies and Integration
Depends on FSAL support for special-file creation and export file-handle generation. It integrates with export quota policy and NFSv3 WCC requirements similarly to `MKDIR`/`SYMLINK`, but with type-specific raw-device handling.

## Risks and Test Signals
Risks include rejecting or mishandling unimplemented NFSv3 type variants, raw device major/minor conversion errors, backend-specific permission constraints for device nodes, and leaked handles on partial success. Test signals are FIFO/socket/char/block creation, invalid type handling, quota denial, non-directory parent, default mode behavior, handle freeing on success, and WCC before/after changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_mknod.c -->
