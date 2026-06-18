# File Research: sources/os/bsd/netbsd-src/lib/libutil/ttymsg.c

## Purpose
Writes vectored messages to terminal devices, with timeout handling for blocking writes.

## Key Details
- Validates `iovcnt` and rejects line names containing `.` or unsafe `/` components.
- Opens `/dev/<line>` nonblocking for write.
- Ignores normal inaccessible/busy tty cases.
- Verifies the fd is a tty.
- Handles partial `writev` progress by adjusting local iovecs.
- On `EWOULDBLOCK`, forks a child, switches to blocking mode, and arms an alarm timeout.
- Returns `NULL` on success or ignored normal errors; otherwise returns a static error string.

## Dependencies and Role
- Used by terminal broadcast/messaging tools.
