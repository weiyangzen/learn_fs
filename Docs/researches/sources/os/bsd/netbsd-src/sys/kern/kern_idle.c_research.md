# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_idle.c

Read completely: 131 lines.

Implements the machine-independent idle LWP loop and idle LWP creation for each CPU.

Idle loop:
- `idle_loop()` runs as the per-CPU idle LWP. It marks the CPU running in `kcpuset_running`, updates the LWP start time, sets scheduler flags, converts the LWP to `LSIDL`, drops to `spl0()`, and then loops forever.
- Each loop iteration asserts that the current LWP/CPU is the idle context, no preemption disable is held, priority is `PRI_IDLE`, and the CPU is idle.
- It calls `sched_idle()`, gives UVM a chance to perform idle work through `uvm_idle()` when the CPU is not offline, enters the MD `cpu_idle()` path if no runnable LWP exists, and otherwise switches to runnable work through `mi_switch()`.

Idle LWP creation:
- `create_idle_lwp()` creates a bound `KTHREAD_IDLE`/`KTHREAD_MPSAFE` kernel thread on the target CPU with `PRI_IDLE`.
- It marks the LWP `LW_IDLE`, stores it in `ci->ci_data.cpu_idlelwp`, and for secondary CPUs pre-sets `LSIDL`, `LP_RUNNING`, and `ci_onproc` because MD CPU startup may enter the idle LWP directly before normal scheduler switching.

Concurrency and integration:
- Relies on scheduler per-CPU lock state and assertions around `spc_lwplock`.
- Integrates with `kthread_create()`, UVM idle processing, MD `cpu_idle()`, and scheduler rescheduling flags.

Risks and notes:
- Creation failure is considered fatal and panics.
- The loop deliberately uses `spl0()` on entry because the first thread on a CPU may arrive through unusual MD startup paths.
