# File Research: sources/os/plan9/9front/sys/src/9/lx2k/main.c

LX2K ARM64 kernel entry and platform bring-up. It parses boot arguments from `BOOTARGS`, initializes configuration environment state, starts the first user process, sizes memory and kernel/user pools, starts secondary CPUs through PSCI `CPU_ON`, handles reboot/reset through PSCI and a reboot trampoline, and provides DMA cache flushing.

`main` has separate paths for secondary and boot CPUs. The boot CPU initializes config, memory, console, traps, FPU, GIC, timer, pages, processes, segments, devices, users, MP, MMU ASID/page-table state, and scheduler. `mpinit` maps MPIDR values to Plan 9 CPU indexes and calls `smccall`.

`reboot` migrates to CPU 0, shuts down devices/clock/interrupts, clears secrets, restores identity TTBR, copies `rebootcode`, flushes I/D caches, and jumps.

Notable risks: `MAXMACH` is one in `mem.h`, so MP scaffolding exists but normally does not start additional CPUs; boot-arg parsing mutates `BOOTARGS` in place.
