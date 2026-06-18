# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_sig.c

Implements signal-related syscall front ends and common helpers for signal actions, masks, pending sets, suspension, alternate stacks, signal delivery requests, user contexts, and timed signal waits.

Key syscall wrappers:
- `sys___sigaction_sigtramp`: copies in/out `sigaction` and delegates to `sigaction1`, including trampoline pointer/version handling.
- `sys___sigprocmask14`: copies an optional mask, applies `sigprocmask1` under `p_lock`, and copies out the old mask.
- `sys___sigpending14`: returns combined process/LWP pending signal set.
- `sys___sigsuspend14`: copies optional temporary mask and delegates to `sigsuspend1`.
- `sys___sigaltstack14`: copies stack settings and delegates to `sigaltstack1`.
- `sys_sigqueueinfo` and `sys_kill`: build `ksiginfo_t` and call `kill1`.
- `sys_getcontext` / `sys_setcontext`: copy user context out/in; `setcontext` returns `EJUSTRETURN`.
- `sys_____sigtimedwait50`: delegates to `sigtimedwait1`.

Core helpers:
- `kill1`: validates signal metadata and caller identity for queued signals, dispatches to a process, process group, or broadcast path, and handles POSIX zombie success behavior.
- `sigaction1`: validates signal number, flags, trampoline ABI/version, compat module availability, updates action/trampoline metadata, handles `SIGCHLD` flags, updates ignore/catch sets, clears ignored pending signals, and schedules user-return signal checks.
- `sigprocmask1`: implements `SIG_BLOCK`, `SIG_UNBLOCK`, and `SIG_SETMASK`, removing unmaskable signals and marking pending signals for user return.
- `sigpending1`: combines LWP and process pending sets.
- `sigsuspendsetup` / `sigsuspendteardown`: temporarily replace signal masks for `sigsuspend`, `pselect`, and `pollts`.
- `sigsuspend1`: waits until interrupted and returns `EINTR`.
- `sigaltstack1`: validates and updates per-LWP signal alternate stack.
- `sigtimedwait1`: imports wait set and optional timeout, consumes pending signals if present, waits on the process signal-waiter list, updates remaining timeout on interrupt/restart, and copies out `siginfo`.

Concurrency/locking:
- Most signal state mutations happen under `p_lock`.
- LWP flags are updated with `lwp_lock` when pending signals require user-return processing.
- `sigaction1` uses `kernconfig_lock` around compat module autoloading for legacy signal trampoline support.

Research notes:
- This file is process-control infrastructure rather than filesystem code, but it affects blocking syscalls, restart behavior, and signal interruption semantics used by I/O paths.
