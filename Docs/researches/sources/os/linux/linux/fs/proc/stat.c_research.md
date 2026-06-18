# File Research: sources/os/linux/linux/fs/proc/stat.c

## Scope

This file implements `/proc/stat`, including aggregate/per-CPU CPU time, interrupt counts, context switches, boot time, fork count, runnable/blocked process counts, and softirq counts.

## Public And Internal APIs Covered

- Exported idle helper: `get_idle_time()`.
- Internal helpers: `get_iowait_time()`, `show_irq_gap()`, `show_all_irqs()`.
- Display/open callbacks: `show_stat()`, `stat_open()`.
- Proc ops: `stat_proc_ops`.
- Init: `proc_stat_init()`.

## Control Flow And Behavior

- `get_idle_time()` and `get_iowait_time()` prefer NO_HZ CPU time hooks for online CPUs and fall back to cpustat fields when hooks return unavailable or the CPU is offline.
- `show_stat()` fetches boot time and applies time namespace boot offset.
- It sums CPU time and IRQ counters over possible CPUs, while per-CPU `cpuN` lines are emitted for online CPUs.
- Interrupt output starts with total interrupt count and emits per-IRQ counts, filling inactive IRQ gaps with zeroes.
- It emits `ctxt`, `btime`, `processes`, `procs_running`, `procs_blocked`, and total/per-vector softirq counts.
- `stat_open()` sizes the single_open buffer based on online CPUs and IRQ count.

## Dependencies And Risks

- Depends on kernel cpustat, IRQ stats, architecture IRQ stat hooks, scheduler counters, time namespaces, and softirq stats.
- Values are sampled across CPUs and counters without a single global lock, so the report is consistent enough for monitoring but not atomic.
