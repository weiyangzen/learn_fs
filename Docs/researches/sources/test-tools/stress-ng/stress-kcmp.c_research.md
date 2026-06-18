# sources/test-tools/stress-ng/stress-kcmp.c

Purpose: implements `kcmp`, a Linux syscall stressor comparing kernel resources between parent and child processes, including files, VM, file tables, fs context, signal handlers, I/O context, SysV semaphores, and optionally epoll target descriptors.

Important APIs/types/functions: local `SHIM_KCMP_*` enum values mirror `linux/kcmp.h`. `SHIM_KCMP()` wraps `shim_kcmp()`. `KCMP` and `KCMP_VERIFY` macros centralize tolerated errors and verification expectations. Optional epoll setup uses `struct shim_kcmp_epoll_slot`.

Control flow: the stressor opens `/dev/null`, optionally reserves a TCP port and creates an epoll-watched socket, sync-starts, forks a child that waits in `pause()`, and the parent opens a second fd. The loop runs many `kcmp` comparisons across parent/child combinations, optional verification checks same-process comparisons return zero, then issues invalid type, fd, and pid calls. On stop it kills the child and closes resources.

State and persistence behavior: state is process and descriptor state only: `/dev/null` fds, optional socket and epoll fd, a child process, and reserved port bookkeeping. No persistent filesystem data is written.

Dependencies and integration points: requires the `kcmp` syscall; optional epoll path depends on epoll headers and glibc support. It uses stress-ng capability checks, networking helpers, bad-fd generation, fork retry, and kill helpers. Registered as `CLASS_OS`, verification optional.

Risks: `kcmp` often needs `CAP_SYS_PTRACE`; `EPERM` is treated as capability failure and aborts the loop. Namespace, Yama, and LSM policy can alter access. Epoll setup uses a fixed starting port via the stress-ng reservation helper.

Test signals: run as unprivileged and privileged users, with `--verify`, and on kernels with and without epoll target support. Confirm accepted errors are limited to expected `EINVAL`, `ENOSYS`, `EBADF`, and capability failure.
