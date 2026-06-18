# File Research: sources/os/linux/linux/fs/xattr.c

Implements Linux VFS extended attribute dispatch, syscall entry points, permission checks, security-module integration, POSIX ACL routing, and generic in-memory simple-xattr helpers.

Key behavior:
- Resolves xattr names to filesystem-provided `struct xattr_handler` entries via `inode->i_sb->s_xattr` and `IOP_XATTR`.
- Enforces namespace-specific access rules:
  - `security.*` and `system.*` are left mostly to filesystem/LSM logic.
  - `trusted.*` requires `CAP_SYS_ADMIN`.
  - `user.*` is limited by inode type and sticky-directory ownership rules.
  - writes reject immutable, append-only, and unmapped-id inodes.
- Provides VFS set/get/list/remove APIs:
  - `vfs_setxattr`, `__vfs_setxattr_locked`, `__vfs_setxattr_noperm`, `__vfs_setxattr`.
  - `vfs_getxattr`, `vfs_getxattr_alloc`, `__vfs_getxattr`.
  - `vfs_listxattr`.
  - `vfs_removexattr`, `__vfs_removexattr_locked`, `__vfs_removexattr`.
- Handles `security.*` specially:
  - set path clears `S_NOSEC` and can fall back to `security_inode_setsecurity`.
  - get path calls `security_inode_getsecurity` before falling back to filesystem xattrs.
  - list path can synthesize LSM security labels if the filesystem lacks `listxattr`.
- Routes POSIX ACL xattr names away from normal handlers into ACL helpers.
- Converts `security.capability` values through `cap_convert_nscap` for idmapped mounts.
- Breaks inode delegations before mutating xattrs and retries after waiting.
- Implements all legacy and `*xattrat` syscalls:
  - `setxattrat`, `getxattrat`, `listxattrat`, `removexattrat`.
  - pathname, symlink-no-follow, and fd/`AT_EMPTY_PATH` variants.
- Copies user xattr names and values with explicit `XATTR_SIZE_MAX` and `XATTR_LIST_MAX` handling.
- Emits audit and fsnotify events for file-based and successful mutation paths.
- Provides `generic_listxattr` and `xattr_full_name` helpers for filesystems with handler tables.
- Implements `simple_xattr` support:
  - lazy rhashtable allocation keyed by parent list and name.
  - RCU-safe lookup, replace, remove, list, and free paths.
  - optional per-inode limits for count and total value size.
  - listing filters privileged `trusted.*` and MAC labels supplied by LSMs.
  - cache cleanup asserts the hash table is empty before destruction.

Important interactions:
- Filesystems expose xattr namespaces by populating `super_block->s_xattr`.
- Security hooks wrap get/set/list/remove operations.
- Idmapped mounts affect ownership, capability xattr conversion, and write permission.
- `simple_xattr` is reusable infrastructure for pseudo and memory-backed filesystems needing xattrs without on-disk storage.
