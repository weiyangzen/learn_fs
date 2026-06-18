# File Research: sources/teaching/xv6-public/sleeplock.h

Defines `struct sleeplock`.

Fields:
- `locked` state.
- Embedded spinlock protecting the sleep-lock state.
- Debug name.
- Owner process PID.

Used by buffer cache and inode cache.
