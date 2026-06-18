# sources/security-integrity/audit-userspace/src/libev/ev_linuxaio.c

Purpose: implements the experimental Linux AIO `IOCB_CMD_POLL` backend for fd readiness, with epoll as a required fallback. In this bundled configuration it is present but normally disabled by `EV_USE_LINUXAIO 0`.

Important APIs/functions: syscall wrappers `evsys_io_setup`, `evsys_io_destroy`, `evsys_io_submit`, `evsys_io_cancel`, and `evsys_io_getevents` call raw Linux AIO syscalls. Backend hooks are `linuxaio_init`, `linuxaio_modify`, `linuxaio_poll`, `linuxaio_destroy`, and `linuxaio_fork`. Helpers include `linuxaio_nr_events`, `linuxaio_array_needsize_iocbp`, `linuxaio_free_iocbp`, `linuxaio_fd_rearm`, `linuxaio_parse_events`, `linuxaio_get_events_from_ring`, `linuxaio_ringbuf_valid`, `linuxaio_get_events`, and `linuxaio_io_setup`.

Control flow: `linuxaio_init` requires a new enough Linux kernel and a working epoll backend, creates an AIO context, starts an internal epoll watcher for fallback events, and replaces backend hooks with linux AIO handlers. `linuxaio_modify` allocates an iocb per fd, cancels active one-shot polls before resubmitting, switches fds previously handed to epoll back to AIO when possible, records fd/generation in `aio_data`, and queues submissions. `linuxaio_poll` submits queued iocbs, falls back individual unsupported fds to epoll on `EINVAL`, grows/recreates the AIO context on `EAGAIN`, can fall back completely to epoll if setup fails, then fetches completions via ring buffer or `io_getevents` and rearms one-shot polls.

State and persistence: persists the AIO context (`linuxaio_ctx`), sizing iteration, per-fd iocb array, queued submission array, and an internal epoll watcher. Each iocb stores the active poll mask in `aio_buf`, fd in `aio_fildes`, generation-tagged identity in `aio_data`, and uses negative `aio_reqprio` to mark epoll fallback ownership.

Dependencies and integration: requires Linux `<linux/aio_abi.h>`, raw syscall numbers, `<poll.h>`, and the epoll backend. It consumes the same `ANFD` generation and event feeding mechanisms as epoll. `ev_vars.h` and `ev_wrap.h` include its loop fields when enabled or when wrapper generation is requested.

Risks: depends on undocumented kernel ring-buffer layout and underdocumented `IOCB_CMD_POLL` behavior. AIO polls are one-shot, so missed rearming can lose readiness. Error handling is complex: `EINVAL`, `EAGAIN`, `EBADF`, and fork can all migrate state between AIO and epoll. Resource limits can force context recreation or complete backend downgrade. Since the audit-userspace config disables it by default, bitrot risk is higher than for epoll/poll/select.

Test signals: only meaningful when compiled with `EV_USE_LINUXAIO`. Test supported sockets/pipes, unsupported tty/file descriptors, many watchers to hit ring sizing, forced `io_submit` partial failures, ring-buffer and `io_getevents` paths, full epoll downgrade, and fork reinitialization.
