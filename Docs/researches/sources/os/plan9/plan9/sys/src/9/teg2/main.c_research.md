# File Research: sources/os/plan9/plan9/sys/src/9/teg2/main.c

Main C boot and machine-initialization path for the Plan 9 Tegra2 ARM kernel.

Key behavior:
- Parses boot arguments and low-memory `plan9.ini` configuration.
- Initializes `Mach` structures, active CPU accounting, caches, L2 page allocator, MMU, traps, memory sizing, clock/timers, devices, PCI, paging, swap, and first user process.
- Creates the first process with stack/text segments and copies `initcode`.
- Starts secondary CPUs after user-process infrastructure is ready.
- Implements shutdown, exit, and reboot through the low-memory reboot trampoline.
- Provides `confinit`, `isaconfig`, `idlehands`, `wakewfi`, and CPU active/offline helpers.

Important functions:
- `main()`: complete bootstrap sequence.
- `mach0init`, `machinit`, `launchinit`: CPU/Mach setup.
- `confinit`: memory and kernel pool sizing.
- `userinit`, `init0`, `bootargs`: first process setup.
- `reboot`: coordinated shutdown and trampoline execution.

Notes:
- Assumes TrimSlice/Tegra2-style 1 GiB DRAM, then verifies memory by probing.
- Uses cache writeback/invalidation aggressively for stability.
