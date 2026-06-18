# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4getroot.c

This small file implements `nfs4_get_rootfh()`, the helper that retrieves and validates an NFSv4 root filehandle during server setup.

Behavior:
- Allocates an `nfs_fattr`.
- Calls `nfs4_proc_get_rootfh()` to fetch the server root filehandle and attributes.
- Verifies that the returned object has a valid type attribute and is a directory.
- Copies the returned fsid into `server->fsid`.
- Frees attributes before returning.

Dependencies:
- `nfs4_proc_get_rootfh()` from the NFSv4 procedure layer.
- `nfs_alloc_fattr()` / `nfs_free_fattr()`.
- `NFS_ATTR_FATTR_TYPE` and `S_ISDIR()` validation.

Risk areas:
- A non-directory root is converted to `-ENOTDIR`.
- Attribute allocation failure returns `-ENOMEM`.
- This function is called during common server setup, so failures abort mount/referral setup early.
