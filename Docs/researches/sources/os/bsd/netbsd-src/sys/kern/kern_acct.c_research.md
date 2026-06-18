# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_acct.c

## Purpose
Implements BSD process accounting: enabling/disabling accounting files, monitoring free space, and writing accounting records on process exit.

## Main Interfaces
- `acct_init()` initializes global accounting state and lock.
- `sys_acct()` authorizes accounting changes, opens/truncates-validates the accounting file, swaps accounting state, stores credentials, and starts the watcher thread.
- `acct_process()` writes one `struct acct` record at process exit.
- `acctwatch()` periodically checks filesystem free space and suspends/resumes accounting.
- `acct_stop()` closes the accounting vnode and releases credentials.
- `acct_chkfree()` compares available blocks against suspend/resume thresholds.
- `encode_comp_t()` encodes elapsed/user/system times and I/O counts into BSD compact accounting format.

## Dependencies
Uses kauth authorization, vnode open/close/getattr/setattr/statvfs, process resource usage, credentials, tty/session state, kernel threads, rwlocks, syslog, and syscall argument definitions.

## Implementation Notes
`acct_lock` serializes syscalls and watcher/thread state. Accounting is suspended below `acctsuspend` percent free blocks and resumed above `acctresume`. `sys_acct()` truncates partial trailing accounting records when reusing an existing file. `acct_process()` temporarily raises `RLIMIT_FSIZE` to avoid user file-size limits preventing kernel accounting writes.

## Research Notes
The major correctness concerns are vnode lifetime during forced unmounts, watcher shutdown, credential ownership for writes, and avoiding deadlocks around process locks and accounting file I/O. This file is part of process-exit behavior, so failures must be logged without destabilizing exit.
