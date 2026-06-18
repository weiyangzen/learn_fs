# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_interrupt.c

Read completely: 497 lines.

Implements machine-independent interrupt-control sysctls used by `intrctl`. It can list interrupt IDs, assigned CPUs, and per-CPU counts; set interrupt affinity; and mark a CPU as accepting or avoiding interrupts through scheduler-state shielding.

Core paths:
- `interrupt_shield()` changes `SPCF_NOINTR` on a target CPU, using an xcall when needed.
- `interrupt_avert_intr()` moves assigned interrupts away from a CPU to available CPUs.
- `interrupt_intrio_list_size()` and `interrupt_intrio_list()` build variable-sized `intrio_list` snapshots.
- Sysctls under `kern.intr` provide `list`, `affinity`, `intr`, and `nointr`.
- Authorization uses `KAUTH_SYSTEM_INTR` for affinity and `KAUTH_SYSTEM_CPU` for CPU interrupt state.

Risks and notes:
- `intr`/`nointr` accept a cpuset but use only the first CPU.
- Interrupt list generation can return `EAGAIN` if interrupts are added after size calculation.
- `nointr` first shields the CPU, then attempts migration; if no destination CPU is available, migration fails.
