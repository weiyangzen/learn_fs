# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_create.c

Purpose: this file implements GPFS filesystem object creation helpers: regular file creation, create-with-POSIX-flags for open2, directory creation, hardlink creation, and special node creation.

Important APIs and functions: `GPFSFSAL_create()` converts FSAL access mode to Unix mode, applies export umask, calls `fsal_internal_create()` with `S_IFREG`, and fetches attributes. `GPFSFSAL_create2()` accepts a Unix mode and POSIX flags from open2, calls the same internal create helper, and optionally fetches attrs. `GPFSFSAL_mkdir()` creates directories with `S_IFDIR`. `GPFSFSAL_link()` checks export link support and calls `fsal_internal_link_fh()` against the destination directory handle. `GPFSFSAL_mknode()` converts FSAL node types to Unix `S_IFBLK`, `S_IFCHR`, `S_IFSOCK`, or `S_IFIFO`, builds a device number for block/character files, calls `fsal_internal_mknode()`, and returns attrs.

Control flow: each mutating operation validates required pointers, converts mode/device inputs, switches to caller credentials with `fsal_set_credentials()`, invokes the lower internal openhandle operation, restores Ganesha credentials, and retrieves post-create attrs on success.

State and persistence: successful operations persist filesystem entries in GPFS and return GPFS file handles. The file itself stores no long-lived state. Attribute outputs are populated through `GPFSFSAL_getattrs()` using the parent object's filesystem private data.

Dependencies and integration: depends on GPFS internal creation/link/mknode wrappers, `GPFSFSAL_getattrs()`, FSAL access/mode helpers, export umask/link capability, and `op_ctx` credentials/export.

Risks and test signals: `fsal_attr` is documented optional in comments, but `GPFSFSAL_create()` and similar functions pass it to `GPFSFSAL_getattrs()` unconditionally after success, so callers should supply a valid attrlist or confirm lower code tolerates NULL. Device construction uses a manual `(major << 20) | minor` layout instead of `makedev()`, which may be platform-sensitive. Tests should cover null argument faults, umask application, create2 with `O_EXCL`/`O_CREAT`, mkdir attrs, link disabled support, invalid node types, missing device for block/char nodes, credential restore on lower failure, and post-create getattr errors.
