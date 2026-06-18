# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_acct.c

Process accounting implementation.

Key behavior:
- `sys_acct()` enables or disables accounting after root check.
- Opens accounting file for append/write, requires a regular vnode, and stores it in `acctp`.
- Uses `acct_lock` to protect active and suspended accounting vnodes.
- `acct_process()` writes one accounting record on process exit, including command, user/system/elapsed time, memory, disk I/O counts, UID/GID, tty, flags, and pid.
- Uses `vn_rdwr()` with `IO_APPEND | IO_UNIT | IO_NOLIMIT`.
- `encode_comp_t()` converts time/count values into historical compact accounting format.
- `acct_thread()` periodically checks filesystem free space with `VFS_STATFS`, suspending below `acctsuspend` percent and resuming above `acctresume`.
- Handles forcibly unmounted accounting files by checking `VBAD`.
- `acct_shutdown()` closes accounting vnode during shutdown.

Filesystem/OS relevance:
- Direct interaction between process accounting and filesystem free-space state.
- Shows vnode lifecycle, append writes, statfs checks, and mount-removal resilience.
