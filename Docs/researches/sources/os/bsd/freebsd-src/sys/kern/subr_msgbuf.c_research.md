# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_msgbuf.c

## Purpose
Provides generic circular kernel message buffer support used by printk/logging and `/dev/klog`.

## Main Interfaces
- `msgbuf_init()`, `msgbuf_reinit()`, `msgbuf_clear()`.
- Writers: `msgbuf_addchar()`, `msgbuf_addstr()`.
- Readers: `msgbuf_getchar()`, `msgbuf_getbytes()`, `msgbuf_peekbytes()`.
- Utilities: `msgbuf_getcount()`, `msgbuf_copy()`, `msgbuf_duplicate()`.

## Implementation Notes
The buffer uses read/write sequence numbers modulo `size * 16`, not plain indices. This preserves ordering across wraps while keeping arithmetic bounded. `msgbuf_getcount()` clamps unread length to buffer size, treating overwritten data as lost.

`msgbuf_reinit()` attempts to preserve old content when magic, size, and checksum match. On mismatch, it clears the buffer and optionally reports the failure when bootverbose is enabled. Reinit assumes old contents did not end in a newline, setting `MSGBUF_NEEDNL`.

`msgbuf_addstr()` handles priority prefixes (`<pri>`), optional timestamps, carriage-return filtering, newline tracking, and insertion of a newline when priority changes mid-line. Timestamps are controlled by `kern.msgbuf_show_timestamp`.

All public read/write operations acquire the message buffer spin mutex. `msgbuf_duplicate()` copies both metadata and backing bytes while holding the source lock.

## Dependencies
Uses `struct msgbuf`, spin mutexes, sysctl, time uptime/microtime, and helper macros in `sys/msgbuf.h`.

## Research Notes
This file is the core data structure behind kernel logging. It supports crash/boot continuity by checksum-based recovery and careful wrap handling.
