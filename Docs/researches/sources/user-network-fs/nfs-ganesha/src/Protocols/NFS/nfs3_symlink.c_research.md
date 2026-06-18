<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c

## Purpose
Implements NFSv3 `SYMLINK`, creating a symbolic link with client-supplied target data and returning optional handle, attributes, and parent WCC.

## APIs, Types, and Functions
Exports `nfs3_symlink()` and `nfs3_symlink_free()`. It uses `SYMLINK3args`, `SYMLINK3resok`, `SYMLINK3resfail`, `nfs3_Sattr_To_FSALattr()`, `squash_setattr()`, export inode quota checking, `fsal_create()` with type `SYMBOLIC_LINK`, `nfs3_FSALToFhandle()`, `nfs_SetPostOpAttr()`, and `nfs_SetWccData()`.

## Control Flow, State, and Persistence
The handler resolves the parent, captures pre-op attributes, validates parent directory type, checks inode quota, validates link name and non-empty target, converts and squashes attributes, ensures a mode is present, and calls `fsal_create()` with the link target string. Success returns a post-op handle, object attributes, and parent WCC; failure maps FSAL status and returns parent WCC where available. Persistent state is the newly created symlink.

## Dependencies and Integration
Depends on FSAL symlink creation support, quota policy, credential squashing, file-handle encoding, and XDR cleanup of dynamically allocated handles. It follows the same create/WCC pattern as `MKDIR` and `MKNOD`.

## Risks and Test Signals
Risks include validating target content too strictly or too loosely relative to NFSv3 expectations, default mode behavior, quota ordering, handle leaks, and backend symlink length limits. Test signals are normal symlink creation, empty name or target, non-directory parent, quota denial, handle-encoding failure, long target handling, and WCC/attribute correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_symlink.c -->
