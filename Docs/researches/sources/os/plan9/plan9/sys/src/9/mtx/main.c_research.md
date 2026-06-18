# File Research: sources/os/plan9/plan9/sys/src/9/mtx/main.c

Defines the MTX PowerPC kernel bootstrap, first user process setup, machine-dependent process hooks, and minimal configuration parsing.

Key points:
- `main()` clears BSS, initializes one CPU, early I/O, i8250 serial console, formatting, configuration, Raven bridge, traps, MMU, interrupts, clock, keyboard, process/page/swap systems, FP save area, first user process, then enters the scheduler.
- `machinit()` initializes `Mach`, sets CPU type from PVR, installs a temporary delay loop constant, enables HID0 caches, and marks CPU 0 active.
- `cpuidprint()` identifies only PowerPC 604e explicitly.
- Provides a static fallback `plan9ini[]` with `console=0` and `ether0=type=2114x`; `getconf()` reads from it.
- `init0()` enters low IPL, builds initial `/` and `.` channels, initializes devices, sets kernel environment variables (`terminal`, `cputype`, `service`), starts `alarm` and `mmusweep`, then jumps to user mode.
- `userinit()` creates the first proc, kernel/user stacks, one text page containing `initcode`, and readies it.
- `confinit()` sizes process, image, swap, page, and malloc pools from ROM-provided `memsize`, with different policy for terminals vs CPU servers.
- Provides MTX versions of `reboot()`, `exit()`, `procsetup()`, `procsave()`, `isaconfig()`, `cistrcmp()`, and `cistrncmp()`.

Dependencies and interactions:
- Uses `raveninit()`, `trapinit()`, `mmuinit()`, `hwintrinit()`, `clockinit()`, and Plan 9 port allocators/device setup.
- `isaconfig()` feeds ISA-like configuration to Ethernet/UART style drivers from `getconf()`.
- `mmusweep` is spawned here and implemented in `mmu.c`.
- `initcode` and `touser()` provide the initial user transition.

Research relevance:
- This is the MTX port’s top-level boot and configuration file, linking machine setup to the portable Plan 9 kernel.
