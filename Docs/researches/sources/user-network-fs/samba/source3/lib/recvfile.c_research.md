# sources/user-network-fs/samba/source3/lib/recvfile.c

## Purpose
This file implements Samba's low-level receive-file helper: read bytes from a socket/file descriptor and write them to a destination fd below the VFS layer. It optionally uses Linux `splice` and otherwise falls back to a buffered userspace loop.

## Important APIs, Types, And Functions
`sys_recvfile(int fromfd, int tofd, off_t offset, size_t count)` returns bytes written or `-1` on read/initial-write error. `default_sys_recvfile()` seeks the output fd unless appending or pipe-like, reads chunks up to `TRANSFER_BUF_SIZE`, and writes with `sys_write()`. `drain_socket()` consumes and discards bytes from a blocking socket, restoring original flags afterward.

## Control Flow
The fallback loop handles `EINTR` on reads, distinguishes first-read `EAGAIN/EWOULDBLOCK` from partial progress, stops writing after a write error while continuing to drain already-read input, and returns the saved write errno. The Linux `splice` branch is effectively disabled initially by `try_splice_call = false`; if enabled, it splices from input to a static pipe and then to the output fd, falling back on unsupported errors and draining the socket when output fails after some input has been consumed.

## State And Persistence
Durable state is file content written to `tofd`. Static state in the splice path includes `pipefd` and `try_splice_call`, shared process-wide and not thread-protected. Socket blocking flags are temporarily changed only by `drain_socket()`.

## Dependencies And Integration Points
It uses Samba `sys_read`, `sys_write`, `set_blocking`, and `VFS_PWRITE_APPEND_OFFSET` constants, plus Linux `splice` when available. SMB server write paths use this for efficient network-to-file transfer.

## Risks And Test Signals
Risk areas are short read/write semantics, preserving errno after write failure, static pipe sharing, blocking-mode restoration, and the disabled splice path. Tests should cover zero count, non-blocking first-read EAGAIN, partial progress before EAGAIN, write failure after input consumption, append offset, ESPIPE seek tolerance, and `drain_socket()` flag restoration.
