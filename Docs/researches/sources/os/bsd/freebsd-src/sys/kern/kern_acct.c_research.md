# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_acct.c

## Purpose
Implements BSD process accounting: `acct(2)` enable/disable, process-exit record generation, accounting-file free-space monitoring, and accounting sysctls.

## Key Elements
- Main syscall: `sys_acct()`.
- Exit hook entry point: `acct_process(struct thread *td)`.
- Accounting state: `acct_vp`, `acct_cred`, `acct_flags`, `acct_configured`, `acct_suspended`.
- Synchronization: `acct_sx`.
- Monitoring thread state: `acct_state` with `ACCT_RUNNING` and `ACCT_EXITREQ`.
- Sysctls: `kern.acct_suspend`, `kern.acct_resume`, `kern.acct_chkfreq`, `kern.acct_configured`, `kern.acct_suspended`.

## Enabling And Disabling
`sys_acct()`:
- Requires `PRIV_ACCT`.
- Opens the target path for append with `NOFOLLOW`.
- Requires a regular vnode.
- Applies MAC checks when enabled.
- Serializes replacement or disable through `acct_sx`.
- Closes the previous accounting file with `acct_disable()`.
- Saves vnode, credential, and flags for the active accounting file.
- Starts the low-priority accounting monitor kproc if needed.
- Treats file replacement as log rotation and avoids redundant enable/disable logs.

Passing `NULL` disables accounting and requests monitor-thread exit.

## Process Record Generation
`acct_process()`:
- Uses a lockless fast-path check before taking `acct_sx`.
- Fills `struct acctv3` on process exit.
- Records controlling tty, command name, user/system CPU time, start time, elapsed time, average memory, block I/O count, uid/gid, and accounting flags.
- Encodes time and long values into IEEE-754 single-precision bit patterns using `encode_timeval()` and `encode_long()`.
- Writes with `vn_rdwr(..., IO_APPEND | IO_UNIT, acct_cred, ...)`.
- Marks the thread with `TDP2_ACCT` while accounting is in progress.

## Space Monitoring
`acctwatch()`:
- Handles disabled or forcibly invalidated accounting vnodes.
- Uses `VFS_STATFS()` on the accounting file's mount.
- Suspends accounting below `kern.acct_suspend` percent available blocks.
- Resumes above `kern.acct_resume` percent available blocks.

`acct_thread()` runs at low priority, periodically calls `acctwatch()`, sleeps on `acct_state`, and exits when requested.

## Research Notes
The conversion block is explicitly marked for regression testing. The active vnode and credential lifetime is protected by `acct_sx`; callers should not touch `acct_vp` without observing that locking design.
