# File Research: sources/os/linux/linux/fs/nfs/export.c

## Role

`export.c` implements `export_operations` for re-exporting an NFS mount through Linux exportfs. It converts NFS inodes to export file handles and reconstructs dentries from those handles.

The exported operations structure is `nfs_export_ops`.

## File Handle Encoding

`nfs_encode_fh()` writes an export file handle containing:
- high 32 bits of the NFS fileid,
- low 32 bits of the fileid,
- inode type bits,
- embedded server NFS filehandle.

It deliberately uses `EXPORT_OP_NOSUBTREECHK`; comments state subtree checking is avoided because embedding parent filehandles may exceed available handle space.

If caller-provided storage is too small, it updates `*max_len` with the required length and returns `FILEID_INVALID`.

## File Handle Decoding

`nfs_fh_to_dentry()` validates handle bounds and type length, extracts the embedded NFS filehandle, builds minimal fattr data from stored fileid/type, and first tries `nfs_ilookup()`. If the inode is not already cached, it performs protocol `getattr()` using the embedded filehandle, then obtains an inode with `nfs_fhget()` and returns `d_obtain_alias()`.

Invalid or mismatched handles return `NULL`, which exportfs interprets as stale where appropriate. RPC/getattr failures return `ERR_PTR(ret)`.

## Parent Lookup

`nfs_get_parent()` uses protocol `lookupp` to obtain the parent filehandle and attributes for a dentry’s inode. If the protocol lacks `lookupp`, it returns `-EACCES`. Otherwise it creates the parent inode with `nfs_fhget()` and returns `d_obtain_alias()`.

## Export Flags

`nfs_export_ops.flags` marks NFS export behavior as remote and nonlocal:
`EXPORT_OP_NOWCC`, `EXPORT_OP_NOSUBTREECHK`, `EXPORT_OP_CLOSE_BEFORE_UNLINK`, `EXPORT_OP_REMOTE_FS`, `EXPORT_OP_NOATOMIC_ATTR`, `EXPORT_OP_FLUSH_ON_CLOSE`, and `EXPORT_OP_NOLOCKS`.
