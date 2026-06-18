# File Research: sources/os/bsd/netbsd-src/sys/sys/cpu.h

Declares machine-independent CPU management hooks and scheduler/preemption interfaces.

Key content:
- Includes `<machine/cpu.h>` and `<sys/lwp.h>`.
- Optional MD overrides for `cpu_idle`, `cpu_need_resched`, and CPU iteration.
- CPU lookup/model/state/intr APIs.
- Kernel preemption entry/exit helpers.
- Interrupt accounting and topology functions.
- Globals: `cpu_lock`, `maxcpus`, `cpu_infos`, `kcpuset_attached`, `kcpuset_running`.
- Inline helpers: `cpu_index`, `cpu_name`.
- CPU microcode support under `CPU_UCODE`.
- Reschedule flags: `RESCHED_REMOTE`, `RESCHED_IDLE`, `RESCHED_UPREEMPT`, `RESCHED_KPREEMPT`.

Important behavior:
- Wrapped to exclude most C declarations from `_LOCORE`.
- Acts as MI facade over MD CPU structures.
