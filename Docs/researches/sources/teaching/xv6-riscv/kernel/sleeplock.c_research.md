# File Research: sources/teaching/xv6-riscv/kernel/sleeplock.c

Implements sleeping locks used for long-held resources such as inodes and buffers.

Important behavior:
- `initsleeplock()` initializes the internal spinlock and debug metadata.
- `acquiresleep()` sleeps while locked, then records ownership by PID.
- `releasesleep()` clears ownership and wakes waiters.
- `holdingsleep()` checks whether the current process holds the lock.

Filesystem relevance: inode locks and buffer locks are sleeplocks because filesystem operations may block while holding them. This is a key distinction from spinlocks.
