# sources/user-network-fs/nfs-utils/utils/mount/fstab.c

Purpose: legacy mount-table and fstab support for builds without libmount, including reading `/etc/mtab`, `/proc/mounts`, `/etc/fstab`, and updating `/etc/mtab` safely.

Important APIs: `mtab_is_a_symlink()`, `mtab_is_writable()`, `mtab_does_not_exist()`, `reset_mtab_info()`, `getmntdirbackward()`, `getprocmntdirbackward()`, `getmntdevbackward()`, `getfsfile()`, `getfsspec()`, `lock_mtab()`, `unlock_mtab()`, and `update_mtab()`.

Control flow: file contents are lazily read into circular doubly-linked `struct mntentchn` chains. Lookups scan backward for most recent mount entries or forward through fstab. `lock_mtab()` creates a pid-specific link target and uses hard-link creation plus `fcntl` locks and signal handlers to serialize writers. `update_mtab()` rereads mtab under lock, removes or updates an entry, writes a temp file, fixes mode/ownership, and renames.

State and persistence: cached flags describe mtab existence/symlink status; global linked lists cache mtab/proc/fstab entries. Persistent output is `/etc/mtab` and its lock/temp files, unless mtab is absent, unwritable, or symlinked.

Dependencies and integration: uses nfs mount-entry wrappers, nfs path constants, xcommon allocation/error helpers, and legacy mount/umount flows.

Risks: signal handling in setuid helpers is delicate; stale lock files and mtab symlinks need careful handling. Test signals include concurrent updates, remount entry replacement, umount deletion of last matching entry, missing `/etc/mtab` fallback to `/proc/mounts`, and fstab lookups.
