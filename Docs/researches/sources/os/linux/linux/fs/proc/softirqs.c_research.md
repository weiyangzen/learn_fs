# File Research: sources/os/linux/linux/fs/proc/softirqs.c

## Scope

This file implements `/proc/softirqs`.

## Public And Internal APIs Covered

- Display callback: `show_softirqs()`.
- Init: `proc_softirqs_init()`.

## Control Flow And Behavior

- The output header lists all possible CPUs.
- Each softirq vector row prints the softirq name and per-CPU counters from `kstat_softirqs_cpu()`.
- Init creates a permanent single-show proc entry named `softirqs`.

## Dependencies And Risks

- Depends on kernel softirq names, `NR_SOFTIRQS`, possible CPU iteration, and kernel stat counters.
- Counters are sampled without global synchronization.
