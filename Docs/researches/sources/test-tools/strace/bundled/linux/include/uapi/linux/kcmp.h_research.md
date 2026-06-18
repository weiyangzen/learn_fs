# sources/test-tools/strace/bundled/linux/include/uapi/linux/kcmp.h

Purpose: defines constants and one helper struct for the `kcmp(2)` process-resource comparison syscall.

Important APIs/types/functions: `enum kcmp_type` selects comparison domains such as files, VM, file table, fs context, signal handlers, IO context, SysV semaphores, and epoll target-fd lookup. `struct kcmp_epoll_slot` carries epoll fd, target fd, and target offset for `KCMP_EPOLL_TFD`.

Control flow: userspace calls `kcmp(pid1, pid2, type, idx1, idx2)`. For epoll comparisons, one index points to a `kcmp_epoll_slot` describing the watched target.

State/persistence behavior: syscall is observational and does not mutate compared tasks. Results depend on live process resource sharing and can race with concurrent process activity.

Dependencies/integration: depends on `linux/types.h`; integrates with proc inspection, checkpoint/restore tooling, and strace syscall argument decoding.

Risks and test signals: pid lifetime races and pointer interpretation for epoll slots are key risks. Tests should decode every `KCMP_*` type and validate `kcmp_epoll_slot` printing for `KCMP_EPOLL_TFD`.
