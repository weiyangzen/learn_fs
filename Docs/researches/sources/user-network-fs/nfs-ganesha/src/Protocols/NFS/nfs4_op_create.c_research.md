<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c

## Purpose
Implements NFSv4 `OP_CREATE` for non-regular objects: directories, symlinks, sockets, FIFOs, character devices, and block devices. Regular file creation is intentionally left to `OPEN`.

## APIs, Types, and Functions
Exports `nfs4_op_create()` and `nfs4_op_create_Free()`. It uses `CREATE4args/res`, `nfs4_sanity_check_FH(DIRECTORY)`, `check_quota(FSAL_QUOTA_INODES)`, `nfs4_Fattr_Supported()`, `nfs4_Fattr_Check_Access()`, `nfs4_utf8string_scan()`, `nfs4_Fattr_To_FSAL_attr()`, `fsal_create()`, `nfs4_FSALToFhandle()`, `set_current_entry()`, `fsal_get_changeid4()`, and parent change attributes.

## Control Flow, State, and Persistence
The handler validates the current FH and export quota, checks that requested create attributes are supported and writable, validates the object name, converts fattrs to FSAL attrs, maps `createtype4` to FSAL object type and raw-device/link data, supplies default modes if absent, and calls `fsal_create()`. Success builds a new current FH for the created object, invalidates the current stateid, reports the requested attrset mask, computes change info from FSAL pre/post parent change attributes or fallback change IDs, stores the new object as the compound current entry, and returns `NFS4_OK`. Persistent state is the new namespace object.

## Dependencies and Integration
Depends on FSAL create support, NFSv4 attribute conversion, export quota, UTF-8/path component validation, current FH mutation, and compound current-entry reference management. It integrates with subsequent compound ops by replacing the current FH with the created object.

## Risks and Test Signals
Risks include default mode choices, symlink target validation differences, attrset reporting all requested bits after create, change-info atomic flag accuracy, raw device number handling, and current FH update after partial failures. Test signals are create directory/symlink/FIFO/socket/char/block, regular-file rejection, invalid UTF-8 names, unsupported attrs, quota denial, change info before/after/atomic behavior, and follow-up GETFH/GETATTR in the same compound.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_create.c -->
