# sources/test-tools/stress-ng/stress-pidfd.c

Purpose: `stress-pidfd.c` implements the `pidfd` stressor, exercising Linux pidfd opening, signaling, pidfd getfd, stat, and invalid operation paths against short-lived child processes.

Important APIs/types/functions: the implementation is gated by `HAVE_PIDFD_SEND_SIGNAL`. `stress_pidfd_open()` probes invalid pid/flags and randomly uses `pidfd_open()` or `/proc/$pid` directory open as a fallback pidfd-like descriptor. `stress_pidfd_supported()` validates pidfd send-signal support. `stress_pidfd_reap()` kills/waits a child and closes its pidfd.

Control flow: after sync, the stressor repeatedly forks a paused child. The parent optionally tests `PIDFD_NONBLOCK`, opens a pidfd, `fstat`s it, tries illegal `mmap`, attempts `pidfd_getfd` on fd 0 plus invalid flags/bad fd, sends signal 0 for existence, then SIGSTOP and SIGCONT through `pidfd_send_signal`. It also exercises special pidfd constants when available, reaps the child, and increments bogo ops.

State and persistence behavior: state is a child process per iteration, the pidfd/proc descriptor, and transient file-descriptor copies returned by `pidfd_getfd`. No filesystem output is created, though `/proc` is used for fallback descriptors.

Dependencies and integration points: pidfd syscall shims, procfs, fork retry, bad fd helpers, kill/wait helpers, `stress_unused_racy_pid_get()`, mmap failure probing, sync barriers, and `CLASS_INTERRUPT | CLASS_OS` registration with `VERIFY_ALWAYS`.

Risks: fallback opening `/proc/$pid` may not support every pidfd operation. Child lifetime races can make pidfd open fail and retry. `pidfd_getfd` behavior depends on ptrace permissions and kernel support. ENOSYS during send-signal is converted to not-implemented.

Test signals: direct `--pidfd` should make bogo progress and no send-signal failures. Tests should cover kernels without pidfd syscalls, procfs unavailable, permission-denied `pidfd_getfd`, `PIDFD_NONBLOCK`, and valid SIGSTOP/SIGCONT delivery.
