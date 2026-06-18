# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_generic.c

Implements generic file-descriptor syscalls and helpers: `read`, `readv`, `write`, `writev`, positioned read/write helpers, `ioctl`, `select`, `pselect`, `poll`, `ppoll`, select/poll conversion through per-thread kqueue state, `selwakeup()`, and `utrace`.

I/O vector handling is centralized in `iovec_copyin()` and `iovec_free()`. It copies user iovecs into either stack storage or allocated memory, rejects zero/too many vectors, validates each length and total residual against `SSIZE_MAX`, and emits ktrace structure records when enabled.

`sys_read()`/`sys_readv()` build `uio` structures and call `dofilereadv()`. `dofilereadv()` obtains an `FREAD` file reference, validates positioned-read constraints for vnode/FIFO/TTY and negative offsets, sets user-space read `uio` fields, optionally snapshots iovecs for ktrace, calls `fo_read`, converts partial interrupt/restart/would-block errors to success, updates file read transfer/byte counters under `f_mtx`, emits genio ktrace, returns byte count, and releases the file.

`sys_write()`/`sys_writev()` mirror the read path through `dofilewritev()`. The write helper obtains `FWRITE`, denies `UF_PLEDGEOPEN`, validates positioned writes, calls `fo_write`, converts partial interrupt/restart/would-block errors, sends `SIGPIPE` on `EPIPE`, updates write counters, traces successful writes, and returns bytes written.

`sys_ioctl()` obtains a read/write-capable file, rejects DNS sockets, applies `pledge_ioctl()`, directly handles `FIONCLEX`/`FIOCLEX`, allocates or uses stack ioctl buffers based on `IOCPARM_LEN`, copies in/out according to command direction, special-cases `FIONBIO` and `FIOASYNC`, dispatches to `fo_ioctl`, and copies output back deterministically after zero-initializing output buffers.

`sys_select()` and `sys_pselect()` validate timeout and optional signal masks, then call `dopselect()`. `dopselect()` bounds `nd` by open files, allocates six fd-set buffers, copies in input sets, optionally installs temporary signal mask, initializes kqueue polling, registers selected fds through `pselregister()`, handles empty interest sets by sleeping on `nowake`, otherwise scans the process kqueue and maps ready events back into output fd sets through `pselcollect()`. It copies output sets back, traces fd sets, and tears down kqpoll state.

`pselregister()` converts read/write/exception fd bits into `EVFILT_READ`, `EVFILT_WRITE`, and `EVFILT_EXCEPT` kqueue registrations with `__EV_SELECT`, tolerating unsupported/unimplemented filters. `pselcollect()` validates per-thread serial tagging and maps ready filters back to fd-set bits.

`selwakeup()` submits kqueue notes under the kernel lock. Poll support uses the same kqueue machinery with `pollfd` encoding. `sys_poll()` converts millisecond timeout to timespec; `sys_ppoll()` accepts timespec and signal mask; both call `doppoll()`. `doppoll()` copies pollfd arrays, registers events through `ppollregister()`, sleeps if no events exist, scans kqueue, maps events through `ppollcollect()`, and copies only `revents` back with `pollout()` even for interrupted poll semantics.

`ppollregister()` builds up to three kqueue events per pollfd and uses `ppollregister_evts()` to handle EBADF/POLLNVAL, detach/POLLERR, FIFO write EPERM/POLLHUP fallback, and unsupported filters. `ppollcollect()` decodes `udata` as poll-array index, validates fd identity, maps filter events and hangups to `revents`, avoids double-counting already seen pollfds, and rate-limits warnings for unclaimed events.

`sys_utrace()` forwards user trace records to ktrace when enabled and otherwise returns success.

Filesystem relevance: this file is a primary syscall boundary into file and vnode operations. It invokes file operation vectors (`fo_read`, `fo_write`, `fo_ioctl`), handles vnode-specific positioned I/O validation, maintains per-file I/O counters, interacts with sockets/devices/FIFOs/TTYs, and implements readiness notification over kqueue for descriptors used by filesystems and storage-backed objects.
