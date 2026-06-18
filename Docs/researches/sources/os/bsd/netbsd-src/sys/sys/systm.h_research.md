# File Research: sources/os/bsd/netbsd-src/sys/sys/systm.h

Read completely: 781 lines.

Central NetBSD kernel system declaration header.

Key elements:
- Declares global kernel identity, memory, CPU, root, dump, swap, and console state.
- Defines `struct sysent`, syscall entry flags, syscall argument access via `SCARG`, and syscall tracing/debug hooks.
- Provides generic stub routines such as `nullop`, `enodev`, `enosys`, `enoioctl`, and `eopnotsupp`.
- Declares kernel formatting/logging APIs, panic paths, device/interface `aprint_*` helpers, and byte formatting helpers.
- Declares copyin/copyout, kcopy, user fetch/store, and user compare-and-swap APIs, with KASAN/KCSAN/KMSAN wrapper selection.
- Declares clock initialization, hardclock/statclock/profiling, NTP/PPS hooks, root filesystem hooks, shutdown/power/exec/exit/fork hooks, and `uiomove` helpers.
- Defines console magic sequence state and debugger entry macros.
- Declares kernel lock, configuration lock, preemption control, and sleepability assertion helpers.

Risks and notes:
- This header is a high-fanout kernel interface; changes can affect nearly every subsystem.
- Syscall flags and argument layout are ABI- and MD-sensitive.
- Copyin/copyout and sanitizer indirections are security-critical user/kernel boundary code.
