# File Research: sources/os/linux/linux/io_uring/epoll.c

## Purpose
Implements io_uring epoll control and epoll wait opcodes.

## Main Functions
- `io_epoll_ctl_prep()`: validates SQE fields, extracts epfd/op/fd, and copies `epoll_event` from userspace when required.
- `io_epoll_ctl()`: calls `do_epoll_ctl()` and supports nonblocking `-EAGAIN` retry behavior.
- `io_epoll_wait_prep()`: validates SQE fields and stores maxevents/events pointer.
- `io_epoll_wait()`: calls `epoll_sendevents()` and returns `-EAGAIN` if no events are ready.

## Important Design Points
- `io_epoll_ctl()` respects `IO_URING_F_NONBLOCK` via `force_nonblock`.
- `io_epoll_wait()` is naturally retryable when no events are available.
- Prep rejects unused SQE fields to preserve ABI strictness.

## Cross-File Relationships
- Declarations are in `epoll.h`.
- Compiled only with `CONFIG_EPOLL`.
- Uses core eventpoll helpers from the kernel epoll subsystem.

## Risks / Review Notes
- `copy_from_user()` is done during prep for event-bearing epoll ctl operations.
- `epoll_wait` stores userspace event pointer and relies on issue-time helper behavior.
