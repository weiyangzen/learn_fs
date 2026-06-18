# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/empty_check_hsm.c

Purpose: this file supplies the default non-Lustre HSM check hook for FSAL_VFS.

Important function: `check_hsm_by_fd(int fd)` ignores its file descriptor and returns `ERR_FSAL_NO_ERROR`.

Control flow and state: VFS open paths call this hook after opening a file. In the plain VFS module, this implementation makes HSM checks a no-op so opens continue normally.

Dependencies and integration points: included in `fsalvfs` target by `vfs/CMakeLists.txt`; the Lustre variants instead use `llapi_check_hsm.c`.

Risks: the hook must remain ABI-compatible with the Lustre implementation. Plain VFS will never return `ERR_FSAL_DELAY` for offline files.

Test signals: build plain FSAL_VFS and verify opens do not depend on Lustre headers or `lustreapi`, and that `vfs_open2_by_handle`/`vfs_open2` proceed after the no-op check.
