# File Research: sources/os/linux/linux-stable/fs/signalfd.c

## Purpose

Implements `signalfd` and `signalfd4`, exposing selected pending signals as records readable from an anonymous inode file descriptor.

## Main Responsibilities

- Defines `struct signalfd_ctx`, storing the signalfd signal mask.
- Implements lifecycle and readiness:
  - `signalfd_release()` frees per-file context.
  - `signalfd_poll()` waits on the current sighand signalfd waitqueue and reports `EPOLLIN` if matching private or shared pending signals exist.
  - `signalfd_cleanup()` wakes pollfree waiters when a sighand is detached.
- Converts kernel signal info to ABI records:
  - `signalfd_copyinfo()` fills fixed-size `struct signalfd_siginfo` according to `siginfo_layout()`.
  - Handles kill, timer, poll, fault, child, realtime, and syscall signal layouts.
- Implements reads:
  - `signalfd_dequeue()` dequeues matching signals, optionally sleeps, and handles nonblocking and interruptible waits.
  - `signalfd_read_iter()` emits one or more `signalfd_siginfo` records, requiring the read size to include at least one full record.
- Implements fdinfo support under `CONFIG_PROC_FS` by rendering the inverse mask shown as `sigmask`.
- Implements syscall creation/update:
  - `do_signalfd4()` validates flags, removes uncatchable signals from the mask, inverts it for internal matching, creates an anonymous inode fd, or updates an existing signalfd context.
  - `signalfd4()` and `signalfd()` copy native masks from userspace.
  - Compat syscalls copy `compat_sigset_t` masks.

## Key Data/Control Flow

- The user-supplied mask is normalized by deleting `SIGKILL` and `SIGSTOP`, then inverted with `signotset()` before storage.
- Poll and dequeue operate under `current->sighand->siglock` while checking/dequeueing pending signals.
- Blocking reads add a waitqueue entry to `current->sighand->signalfd_wqh`, set `TASK_INTERRUPTIBLE`, and loop until a matching signal, pending interruption, or error.
- Multi-record reads make the first dequeue obey file nonblocking/nowait state and subsequent dequeues nonblocking to avoid partial-read blocking.

## ABI and Integration Notes

- The signalfd record size is compile-time asserted to 128 bytes.
- Uses `anon_inode_getfile_fmode()` and `FD_ADD()` for new fd creation.
- Reusing an fd requires that it already be backed by `signalfd_fops`.
- `SFD_CLOEXEC` and `SFD_NONBLOCK` are compile-time checked against `O_CLOEXEC` and `O_NONBLOCK`.

## Correctness and Risk Notes

- Updating an existing signalfd mask is done under `siglock` and wakes the signalfd waitqueue.
- Synchronous fault-specific layouts are treated as generic fault layouts if such signals are injected and caught through signalfd.
- `copy_to_iter_full()` failure returns `-EFAULT`; partial records are not exposed.
