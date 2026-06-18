<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c

## Purpose
Implements NFSv3 `LINK`, creating a hard link to an existing object in a target directory while returning weak cache consistency data for the destination directory and attributes for the linked object.

## APIs, Types, and Functions
The main functions are `nfs3_link()`, `nfs3_link_free()`, and the internal `nfs3_verify_exportid()`. It uses `LINK3args`, `LINK3res`, `fsal_attrlist`, `pre_op_attr`, `nfs3_FhandleToExportId()`, `nfs3_FhandleToCache()`, `fsal_link()`, `nfs_SetPostOpAttr()`, `nfs_SetWccData()`, and `nfs_PreOpAttrFromFsalAttr()`.

## Control Flow, State, and Persistence
Before object lookup, `nfs3_verify_exportid()` rejects malformed handles and cross-export hard links with `NFS3ERR_BADHANDLE` or `NFS3ERR_XDEV`. The handler resolves the destination directory and source object, captures destination pre-change attributes, validates directory type and link name, then calls `fsal_link()` with pre/post directory attribute outputs. Success returns target object post-op attributes and destination WCC; failure maps FSAL status and still attempts to fill target attributes and WCC. Object references and prepared attributes are always released.

## Dependencies and Integration
The handler depends on export IDs encoded in NFSv3 file handles, FSAL hard-link support, object-cache reference handling, and NFSv3 WCC helpers. It integrates with export isolation policy by refusing links across exports before the FSAL call.

## Risks and Test Signals
Risks include export-id parsing mismatches with file-handle formats, link-count or parent WCC races if FSAL pre/post attributes are incomplete, and backends that do not support hard links. Test signals are same-export hard-link creation, cross-export `XDEV`, empty-name `INVAL`, non-directory target parent `NOTDIR`, backend `EOPNOTSUPP` mapping, and reference leak tests on early source-handle failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_link.c -->
