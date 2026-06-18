# File Research: sources/os/linux/linux-stable/fs/afs/xattr.c

## Scope

Exposes AFS metadata and ACL operations through Linux extended attributes.

## APIs And Behavior

- `afs.acl` gets/sets AFS3 ACLs through `afs_fs_fetch_acl()` and `afs_fs_store_acl()`.
- `afs.yfs.acl`, `afs.yfs.acl_inherited`, `afs.yfs.acl_num_cleaned`, and `afs.yfs.vol_acl` expose YFS opaque ACL data and metadata; setting is supported only for `afs.yfs.acl`.
- Read-only xattrs `afs.cell`, `afs.fid`, and `afs.volume` return cell name, formatted FID, and volume name.
- Handler tables publish AFS ACL, metadata, and YFS-prefix handlers for non-dynroot superblocks.

## State And Dependencies

Uses `struct afs_operation`, vnode volume/cell/FID state, AFS and YFS ACL RPCs, status commit on success, and allocated ACL buffers.

## Risks And Invariants

`XATTR_CREATE` is rejected for ACL mutation. YFS unsupported operations are translated from `-ENOTSUPP` to `-ENODATA`. Buffer sizing follows xattr conventions: size zero queries required length, too-small buffers return `-ERANGE`.
