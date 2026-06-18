# File Research: sources/os/plan9/9front/sys/src/9/pc64/main.c

Main PC64 kernel bootstrap, machine initialization, configuration sizing, first user process entry, and reboot support.

Key behavior:
- Defines global `Conf conf` and `idle_spin`.
- `confinit` derives process/image/swap counts, user/kernel memory split, interrupt allocation budget, and pool maximums from physical memory and boot configuration such as `service`, `*kernelpercent`, and `*imagemaxmb`.
- `machinit` initializes per-CPU `Mach` state while preserving CPU number, PML4, and GDT.
- `mach0init` installs bootstrap CPU `Mach`, PML4, and GDT addresses and marks CPU 0 active.
- `init0` initializes devices, sets kernel environment variables, starts the alarm kproc, builds the initial user stack for `boot`, exits kernel FPU context, and calls `touser`.
- `main` performs the boot sequence: early traps, I/O, console, screen, CPU identification, memory initialization, architecture hooks, allocator setup, traps/math, PCI, MMU, interrupts, timers, processes, devices, pages, first user process, and scheduler.
- Reboot support copies trampoline code to `REBOOTADDR`, adjusts mappings/executable permissions, disables interrupts, and jumps into reboot code to relocate or park.

Notable dependencies:
- Almost every PC64 subsystem: traps, MMU, memory, arch hooks, console, PCI, screen, timers, devices, process setup, and reboot trampoline.
- `rebootcode.i`, generated from `rebootcode.s`.

Research notes:
- Boot order is deliberate: early console/screen precede full MMU and interrupt setup, while process/device setup comes after page and pool initialization.
- Memory pool sizing accounts for large kernel structures but explicitly says mount cache and mount RPC allocations are not included in the estimate.
