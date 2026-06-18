# File Research: sources/os/bsd/freebsd-src/sys/fs/fifofs/fifo_vnops.c

## Purpose
Implements named FIFO vnode operations by backing each active FIFO vnode with a kernel pipe.

## Main Elements
- `struct fifoinfo` stores the backing pipe, reader/writer counts, and generation counters.
- Registers `fifo_specops`, where open/close/print/advisory-lock are implemented and most namespace/data VOPs panic or return bad-fd because file operations switch to `pipeops`.
- `fifo_open()` creates the pipe on first open, updates reader/writer counts, handles nonblocking writer `ENXIO`, waits for counterpart readers/writers for blocking opens, defers stop signals while sleeping, handles interrupted opens, and initializes the file as `DTYPE_FIFO` with `pipeops`.
- `fifo_close()` decrements reader/writer counts, sets pipe EOF state, wakes blocked readers/writers and poll/select waiters, advances writer generation, and frees FIFO state when the last endpoint closes.
- `fifo_cleanup()` destroys the pipe and frees state when both counts reach zero.
- `fifo_printinfo()` and `fifo_print()` expose current FIFO state for diagnostics.
- `fifo_advlock()` allows only flock-style advisory locking through `vop_stdadvlock()`.

## Dependencies And Integration
Used by filesystems that map FIFO vnodes to `fifo_specops`, including ext2fs through `ext2_fifoops`. It depends on pipe locking, vnode locking, file initialization, and select/poll wakeups.

## Risk Notes
Correctness depends on combined vnode and pipe locking to avoid missed wakeups while dropping the vnode lock for sleeps. Open interruption paths must undo reader/writer counts consistently.
