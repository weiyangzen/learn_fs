# File Research: sources/teaching/xv6-riscv/kernel/sleeplock.h

Defines `struct sleeplock`.

Fields:
- `locked` indicates ownership.
- Internal `struct spinlock lk` protects sleeplock state.
- `name` and `pid` provide debug ownership metadata.

Filesystem relevance: embedded in `struct inode` and `struct buf` to serialize long-duration filesystem/block access while allowing the holder to sleep.
