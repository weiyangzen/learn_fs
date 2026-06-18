# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.h

Header for mount table helper functions used by `mount.ocfs2`.

Key contents:
- Declares `struct mntentchn`, a doubly linked wrapper around `struct my_mntent`.
- Exposes mtab status, lookup, lock, unlock, and update functions.
- Disables fstab-specific lookup declarations with `#if 0 /* OCFS2 modification */`.

Public declarations:
- `mtab_is_writable`, `mtab_does_not_exist`, `mtab_is_a_symlink`.
- `is_mounted_once`.
- `mtab_head`, `getmntfile`, `getmntoptfile`, `getmntdirbackward`, `getmntdevbackward`.
- `lock_mtab`, `unlock_mtab`, `update_mtab`.

Research notes:
- The header intentionally narrows util-linux-style fstab support to the mtab behavior needed by OCFS2 mount tooling.
