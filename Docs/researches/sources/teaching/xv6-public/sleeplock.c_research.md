# File Research: sources/teaching/xv6-public/sleeplock.c

Implements sleeping locks for long critical sections.

Key behavior:
- `initsleeplock` initializes the embedded spinlock, name, lock state, and owner PID.
- `acquiresleep` sleeps while locked, then marks locked and records current PID.
- `releasesleep` clears state and wakes sleepers.
- `holdingsleep` checks whether current process owns the lock.

Role:
- Used for buffers and inodes where sleeping while waiting is acceptable.
