# File Research: sources/teaching/minix/minix/servers/vfs/lock.h

Header defining the advisory lock table.

`struct file_lock` fields:
- `lock_type`: `F_RDLCK`, `F_WRLCK`, or zero for unused.
- `lock_pid`: owning PID.
- `lock_vnode`: locked vnode.
- `lock_first`: first locked byte.
- `lock_last`: last locked byte.

Declares global `file_lock[NR_LOCKS]`.
