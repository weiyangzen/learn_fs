# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_intr.c

## Role

`cpu_intr.c` provides the architecture-independent CPU interrupt participation helpers. It determines whether CPUs are accepting I/O interrupts, finds alternate interrupt-capable CPUs, counts interrupt-capable CPUs, and wraps machine-dependent interrupt enable/disable operations.

## Functions

`cpu_intr_on()` returns whether a CPU has `CPU_ENABLE` set. It requires `cpu_lock`.

`cpu_intr_next()` walks the online CPU list from a given CPU and returns the next online CPU that accepts interrupts, or `NULL` if none is found.

`cpu_intr_count()` counts CPUs in the all-CPU circular list that currently accept I/O interrupts.

`cpu_intr_enable()` calls the machine-dependent `cpu_enable_intr()` if interrupts are currently disabled for the CPU, then updates user-visible CPU state through `cpu_set_state()`.

`cpu_intr_disable()` prevents taking the last interrupt-capable CPU out of service. If another interrupt-capable CPU exists, it first tries to juggle cyclics away from the target CPU with `cyclic_juggle()`, then calls machine-dependent `cpu_disable_intr()`. On success it updates CPU state.

## Integration

This file is used by CPU online/offline and `p_online(2)` state transitions. `cpu_offline()` depends on `cpu_intr_disable()` to move a CPU out of interrupt participation before quiescing or offlining it.

## Research Notes

The file is intentionally small, but it enforces an important system invariant: the kernel should not gracefully disable I/O interrupt participation on the last interrupt-capable CPU. Platform-specific interrupt routing remains in machine-dependent helpers.
