# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_acct.c

## Summary
Implements BSD process accounting: privileged users can enable accounting to a regular file, and exiting processes append compact accounting records.

## Main Responsibilities
- Implements `acct(2)` via `sys_acct`.
- Opens and tracks the accounting vnode.
- Writes process accounting records from `acct_process`.
- Periodically suspends/resumes accounting based on free filesystem space.
- Provides sysctls for suspend percentage, resume percentage, and check frequency.

## Important Behavior
`sys_acct` requires `SYSCAP_NOACCT`, opens the target path with `FWRITE|O_APPEND`, requires a regular file, closes any previous accounting vnode, and starts `acctwatch`.

`acct_process` snapshots command name, user/system CPU time, elapsed time, memory average, I/O block counts, real uid/gid, controlling tty, and accounting flags. It temporarily removes the process file-size rlimit before appending `struct acct`.

`acctwatch` uses `VFS_STATFS` on the accounting file mount. It moves `acctp` to `savacctp` when free blocks fall below `kern.acct_suspend` and resumes when above `kern.acct_resume`.

## Risks
Accounting relies on a live vnode and mount; forced unmount or `VBAD` causes closure. The code serializes vnode switching with `acct_lock`, but record appends occur while holding that lock, so slow filesystem writes can delay accounting control paths.
