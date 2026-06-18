# sources/user-network-fs/samba/source4/ntvfs/posix/xattr_system.c

Purpose: `xattr_system.c` is the POSIX backend adapter for storing and retrieving Samba metadata in native filesystem extended attributes.

Important APIs, types, and functions: It exports `pull_xattr_blob_system`, `push_xattr_blob_system`, `delete_xattr_system`, and `unlink_xattr_system`. These operate on either a pathname or fd and translate Unix errors through `pvfs_map_errno`.

Control flow: Pull allocates an estimated-size blob, reads with `fgetxattr` or `getxattr`, doubles the allocation on `ERANGE`, and returns a sized `DATA_BLOB`. A special `EPERM` path stats the target and treats sticky directories as not found, matching expected semantics for inaccessible directory xattrs. Push and delete call the fd or path xattr variants and map errors.

State and persistence behavior: Metadata persists in filesystem xattrs. The code holds no global state. `unlink_xattr_system` is a no-op because native xattrs are removed with the file by the filesystem.

Dependencies and integration points: It depends on `pvfs_state`, Samba `DATA_BLOB`, talloc allocation, system xattr APIs, and POSIX stat mode checks. Higher-level `pvfs_xattr` code selects this backend when native xattrs are enabled.

Risks: Estimated-size growth must avoid repeated realloc failures and races with concurrent xattr changes. Filesystem-specific xattr namespaces and permission behavior affect SMB metadata correctness. The sticky-directory EPERM exception is subtle and should not mask real permission bugs outside that case.

Test signals: Tests should force small initial estimates, read changed-size xattrs, use fd and path variants, delete missing attributes, run on sticky directories, and verify error translation for unsupported xattr filesystems.
