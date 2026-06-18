# File Research: sources/os/linux/linux/fs/signalfd.c

Implements `signalfd(2)` and `signalfd4(2)`, exposing pending signals as records readable from an anonymous inode file descriptor.

`struct signalfd_ctx` stores the effective blocked-signal mask. `do_signalfd4()` creates a new anon inode file or updates an existing signalfd, validates `SFD_CLOEXEC`/`SFD_NONBLOCK`, removes uncatchable `SIGKILL`/`SIGSTOP`, then inverts the mask with `signotset()` for internal matching.

`signalfd_poll()` waits on `current->sighand->signalfd_wqh` and checks private and shared pending queues under `siglock`. `signalfd_dequeue()` dequeues or sleeps interruptibly; `signalfd_read_iter()` returns one or more fixed-size `struct signalfd_siginfo` records and switches to nonblocking behavior after the first signal.

`signalfd_copyinfo()` translates `kernel_siginfo_t` layouts into the stable 128-byte userspace ABI, explicitly handling kill, timer, poll, fault, child, realtime, and syscall signal layouts.

Compat syscall wrappers convert `compat_sigset_t` and forward into the native implementation. Proc fdinfo support renders the user-visible signal mask.
