# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fem.c

## Role

Installs and implements FEM vnode monitors used by SMB for file change notification and oplock breaking when non-SMB filesystem activity touches watched SMB nodes.

## Major Responsibilities

- Creates FEM operation vectors for file-change-notification and oplock monitors.
- Installs/uninstalls notification hooks on directory nodes.
- Installs/uninstalls oplock hooks on file nodes with SMB node reference callbacks.
- Emits directory change notifications for non-SMB creates, removes, renames, mkdir/rmdir, links, and symlinks.
- Breaks SMB oplocks before non-SMB open, read, write, truncation, allocation changes, remove, and rename operations.
- Honors caller contexts so SMB-originated VOP calls do not recursively notify or break oplocks.
- Provides bounded oplock wait behavior, including `CC_DONTBLOCK` handling.

## Key Functions

- `smb_fem_init()` creates `smb_fcn_ops` and `smb_oplock_ops`.
- `smb_fem_fini()` frees FEM operation vectors.
- `smb_fem_fcn_install()` and `smb_fem_fcn_uninstall()` manage notification hooks.
- `smb_fem_oplock_install()` and `smb_fem_oplock_uninstall()` manage oplock hooks.
- `smb_fem_fcn_create()`, `smb_fem_fcn_remove()`, `smb_fem_fcn_rename()`, `smb_fem_fcn_mkdir()`, `smb_fem_fcn_rmdir()`, `smb_fem_fcn_link()`, and `smb_fem_fcn_symlink()` call through to `vnext_*()` and notify successful non-SMB namespace changes.
- `smb_fem_oplock_open()`, `smb_fem_oplock_read()`, `smb_fem_oplock_write()`, `smb_fem_oplock_setattr()`, `smb_fem_oplock_space()`, and `smb_fem_oplock_vnevent()` initiate the correct oplock break type before passing through.
- `smb_fem_oplock_wait()` waits for oplock break completion or returns `EAGAIN` for nonblocking contexts.

## Research Notes

The FCN hooks focus on namespace changes, not every metadata change, because broad metadata FEM coverage would be costly. Oplock hooks are specifically for NFS/local/non-SMB callers; SMB paths break oplocks at higher layers before VFS.
