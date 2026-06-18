# File Research: sources/os/linux/linux-stable/fs/nfs/export.c

## Role

`export.c` supplies `export_operations` for re-exporting an NFS mount through Linux exportfs/NFS server mechanisms. It encodes an NFS client inode into a file handle that embeds the server filehandle, and decodes such handles back into dentries.

## File handle format

The encoded handle contains high and low 32-bit portions of the inode's NFS fileid, the inode file type (`S_IFMT`), and an embedded `struct nfs_fh`. `nfs_exp_embedfh()` returns the embedded filehandle area inside the raw `__u32` buffer.

`nfs_encode_fh()` computes the required XDR-quad length from the embedded server filehandle size. If the caller's buffer is too small it updates `*max_len` and returns `FILEID_INVALID`. Otherwise it writes fileid, type, padding, copies the NFS filehandle, updates `*max_len`, and returns the filehandle type equal to the encoded length.

Subtree checking is intentionally disabled because embedding parent filehandles could exceed available filehandle space.

## Decoding and parent lookup

`nfs_fh_to_dentry()` validates handle bounds and type, extracts the embedded filehandle size, builds minimal attributes from encoded fileid and type, and first tries `nfs_ilookup()`. If no inode is cached, it calls the server `getattr` RPC, then creates/fetches the inode via `nfs_fhget()` and returns `d_obtain_alias()`.

`nfs_get_parent()` requires protocol `lookupp` support. It calls LOOKUPP on the child inode, creates/fetches the parent inode with `nfs_fhget()`, and returns an alias dentry.

## Export operation flags

`nfs_export_ops` sets `EXPORT_OP_NOWCC`, `EXPORT_OP_NOSUBTREECHK`, `EXPORT_OP_CLOSE_BEFORE_UNLINK`, `EXPORT_OP_REMOTE_FS`, `EXPORT_OP_NOATOMIC_ATTR`, `EXPORT_OP_FLUSH_ON_CLOSE`, and `EXPORT_OP_NOLOCKS`. These advertise remote filesystem limitations and force conservative behavior around unlink, close, attributes, and locking.

## Failure behavior

Malformed or mismatched handles return `NULL`, which exportfs treats as stale. Allocation failure returns `ERR_PTR(-ENOMEM)`. Failed getattr or LOOKUPP errors propagate as error dentries.
