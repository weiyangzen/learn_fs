# sources/test-tools/strace/bundled/linux/include/uapi/linux/sched.h

## Purpose

Defines task creation flags for `clone`, `clone3`, and `unshare`, plus scheduler policy and flag constants. strace uses this header to decode process-creation bitmasks, `struct clone_args`, and scheduler syscall arguments.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. Classic low 32-bit clone flags include `CSIGNAL`, `CLONE_VM`, `CLONE_FS`, `CLONE_FILES`, `CLONE_SIGHAND`, `CLONE_PIDFD`, `CLONE_PTRACE`, `CLONE_VFORK`, `CLONE_PARENT`, `CLONE_THREAD`, namespace flags, TLS/TID flags, and `CLONE_IO`. `clone3` extends the flag space with `CLONE_CLEAR_SIGHAND`, `CLONE_INTO_CGROUP`, `CLONE_AUTOREAP`, `CLONE_NNP`, `CLONE_PIDFD_AUTOKILL`, and `CLONE_EMPTY_MNTNS`. `CLONE_NEWTIME` and `UNSHARE_EMPTY_MNTNS` are separately documented. `struct clone_args` is versioned by size macros and carries flags, pidfd, tids, exit signal, stack, TLS, set_tid array, and cgroup fd. Scheduler exports include `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `IDLE`, `DEADLINE`, `EXT`, reset-on-fork, and `SCHED_FLAG_*`.

## Control Flow, State, and Integration

Kernel flow is syscall-entry validation of flags and optional `clone_args` fields before creating or unsharing task resources. State effects are process/thread creation, namespace membership, pidfd publication, cgroup placement, signal behavior, and scheduler policy metadata.

## Risks and Test Signals

Risks include treating `CSIGNAL` bits as valid for `clone3`, missing 64-bit flags above bit 31, wrong `clone_args` version sizing, and conflating clone-only and unshare-only empty mount namespace bits. Test signals include strace decode for clone, clone3, unshare, `sched_setattr` policy flags, unknown high-bit clone flags, and short `clone_args` sizes.
