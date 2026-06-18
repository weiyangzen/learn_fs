# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_procdesc.c

## Purpose
Implements FreeBSD process descriptors: file descriptors representing processes for capability-style process management, polling, kqueue exit notification, stat/kinfo reporting, and close-time process cleanup.

## Main Elements
- `procdesc_ops`: file operation table for process descriptor objects; read/write/ioctl/truncate are invalid, while poll, kqueue, stat, close, kinfo, and comparison are supported.
- `procdesc_find()`: resolves a process descriptor fd to a locked live `struct proc`, with Capsicum rights validation.
- `procdesc_pid()`, `kern_pdgetpid()`, `sys_pdgetpid()`: expose the PID associated with a process descriptor.
- `procdesc_new()`, `procdesc_falloc()`, `procdesc_finit()`: allocate descriptor state during `pdfork()` setup and bind it to a `struct file`.
- `procdesc_exit()` and `procdesc_reap()`: synchronize process exit/reap with descriptor state, exit status, wait behavior, select, and kqueue notification.
- `procdesc_close()`: handles last close, marking the descriptor closed, reaping zombies, detaching live processes, reparenting to the reaper, and sending `SIGKILL` unless `PDF_DAEMON` is set.
- `procdesc_poll()` and `procdesc_kqfilter()`: report process-exit readiness with `POLLHUP` and `EVFILT_PROCDESC`/`NOTE_EXIT`.
- `procdesc_stat()`, `procdesc_fill_kinfo()`, `procdesc_cmp()`: provide file metadata, `procstat`/`kinfo_file` details, and `kcmp` ordering.

## Dependencies And Integration
Integrates with `proctree_lock`, process locking, file descriptor allocation, Capsicum rights, audit, kqueue/select, process reparenting/reaping, PID lifecycle tracking, and `pdfork`/process descriptor APIs declared in `procdesc.h`.

## Risk Notes
The close/exit/reap paths are delicate because the descriptor and process each hold references. The code uses `proctree_lock` to serialize descriptor close against process exit and avoids synchronous waiting during close to prevent deadlocks. Last close has strong side effects: it may kill a still-running process and change its parentage.
