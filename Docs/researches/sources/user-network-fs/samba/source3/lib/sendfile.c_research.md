# sources/user-network-fs/samba/source3/lib/sendfile.c

## Purpose
This file wraps platform-specific `sendfile` APIs behind `sys_sendfile()`, optionally sending an SMB header before file data. It provides implementations for Linux, Solaris, HP-UX, FreeBSD/Darwin, AIX, and an `ENOSYS` fallback.

## Important APIs, Types, And Functions
`sys_sendfile(int tofd, int fromfd, const DATA_BLOB *header, off_t offset, size_t count)` returns bytes sent or `-1`. Linux sends the header with `sys_send(..., MSG_MORE)` before calling `sendfile`. Solaris uses `sendfilev` vectors; HP-UX uses header/trailer iovecs; FreeBSD/Darwin uses `sf_hdtr`; AIX uses `send_file`.

## Control Flow
All implementations loop until requested file/header data is sent, retry `EINTR` where appropriate, and switch the socket to blocking mode on `EAGAIN/EWOULDBLOCK` because header plus file data must remain ordered. Socket flags are restored on exit. Linux maps unsupported `ENOSYS`/`EINVAL` after a header was sent to `errno = EINTR` as a signal to upper layers to emulate without disabling sendfile immediately.

## State And Persistence
There is no file-local persistent state. The function advances kernel socket output and reads from the source file at the requested offset. It may temporarily mutate socket blocking flags.

## Dependencies And Integration Points
It depends on platform sendfile headers, Samba `DATA_BLOB`, `sys_send`, and `set_blocking`. It is integrated with SMB read response paths that can avoid copying file data through userspace.

## Risks And Test Signals
Risks include platform API semantic differences, header partial-send accounting, incorrect return values on EOF, blocking flag restoration, AIX null-header handling where the return expression uses `header->length`, and upper-layer interpretation of Linux's artificial `EINTR`. Tests should cover header/no-header sends, non-blocking sockets, partial sends, EOF before count, unsupported syscall fallback, and build coverage for each configured platform branch.
