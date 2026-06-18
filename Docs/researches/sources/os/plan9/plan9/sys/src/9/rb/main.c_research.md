# File Research: sources/os/plan9/plan9/sys/src/9/rb/main.c

RouterBoard MIPS kernel mainline for Plan 9. It performs early board bring-up, fixed boot argument setup, process/user initialization, reboot, shutdown, and memory sizing.

Key responsibilities:
- Initializes RouterBoard boot arguments as `/boot/boot boot`, fixed memory configuration, FP save area, Mach state, kmap, traps, TLB, pages, processes, channels, swap, and the first user process.
- Installs MIPS exception vectors into KSEG0 vector slots and clears bootstrap exception-vector mode.
- Reports MIPS 24K CPU identity, endian mode, FPU presence, TLB entries, and L1 cache geometry.
- Builds the initial user stack and init text segment, then enters user mode through `touser(sp)`.
- Seeds early `/env` settings in `init0`, including `cputype`, `terminal`, `service`, `nobootprompt`, and `nvram`.
- Implements Plan 9 reboot by copying `rebootcode` to `REBOOTADDR`, shutting down devices/interrupts/clocks, and jumping to the trampoline with loaded-kernel physical addresses.
- Implements `exit` by disabling the watchdog, waiting for other CPUs/console output, enabling bootstrap vectors, arming a short watchdog reset, then falling back to ROM.

Important interfaces:
- `main`, `machinit`, `vecinit`, `init0`, `userinit`, `confinit`.
- `parsemipsboothdr` for MIPS boot executable header parsing during `rebootcmd`.
- `reboot`, `exit`, `idlehands`, `procsave`, `procrestore`.

Dependencies and assumptions:
- Assumes a single CPU (`MAXMACH` and `conf.nmach` are 1) and fixed RouterBoard memory size from `MEMSIZE`.
- Relies on MIPS assembly helpers for CP0 access, vectors, cache flushes, status changes, user entry, and watchdog control.
- `getconf` is a stub returning nil; this port hard-codes the boot environment instead of reading a full configuration file from RouterBOOT.

Notable risks:
- Initialization order is strict; traps, kmap, TLB, pages, and channel devices are sequenced explicitly.
- `confinit` computes kernel/user memory before setting several process/image/swap counts, so the exact ordering is part of the port contract.
- Reboot and exit paths run with devices and interrupts being torn down and are sensitive to cache/vector correctness.
