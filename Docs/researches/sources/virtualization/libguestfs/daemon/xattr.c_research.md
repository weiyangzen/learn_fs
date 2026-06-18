# File Research: sources/virtualization/libguestfs/daemon/xattr.c

## Role
Implements Linux extended attribute operations for guest files, including symlink-aware variants and bulk xattr listing.

## Feature Gate
The implementation is compiled when Linux xattr headers and list/get/set/remove xattr APIs are available. Otherwise it expands `OPTGROUP_LINUXXATTRS_NOT_AVAILABLE`.

## Main Operations
- `do_getxattrs()` and `do_lgetxattrs()` list and read all attributes for a path.
- `do_setxattr()` and `do_lsetxattr()` set attributes.
- `do_removexattr()` and `do_lremovexattr()` remove attributes.
- `do_getxattr()` and `do_lgetxattr()` read one attribute value.
- `do_internal_lxattrlist()` returns grouped xattr data for many path names under a base path.
- `copy_xattrs()` copies non-hidden attributes from one path to another.

## Data Handling
- `split_attr_names()` converts Linux’s NUL-separated xattr name buffer into a string vector without duplicating individual names.
- `not_hidden_xattr()` filters out `user.WofCompressedData`, used by NTFS CompactOS/system compression.
- Results are sorted by attribute name.
- Attribute value lengths are checked against `XATTR_SIZE_MAX`.

## Error Handling
Most syscalls run inside `CHROOT_IN`/`CHROOT_OUT`. `do_internal_lxattrlist()` treats some per-file list failures as nonfatal and records a special empty-name entry containing the number of attributes.

## Filesystem/Storage Relevance
This file exposes filesystem metadata beyond POSIX mode/ownership, including SELinux labels, ACL backing attributes, user metadata, and filesystem-specific xattrs.
