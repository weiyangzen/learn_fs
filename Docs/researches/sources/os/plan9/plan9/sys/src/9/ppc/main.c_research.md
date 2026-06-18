# File Research: sources/os/plan9/plan9/sys/src/9/ppc/main.c

PPC Plan 9 kernel mainline, configuration parsing, initial process creation, and machine-independent boot sequencing glue.

Key responsibilities:
- Clears BSS and runs early initialization: `machinit`, `confinit`, allocator, traps, MMU, `plan9.ini`, interrupts, clock/timer, console, printing, process and device initialization, paging, swap, shared segments, FP baseline, first user process, and scheduler.
- Parses `plan9inistr` into a fixed `plan9ini` table and exposes `getconf`.
- Builds initial environment entries in `init0`.
- Creates the first user process with stack segment, text segment, copied `initcode`, and scheduler entry.
- Implements shutdown `exit`, process FP setup/save/restore hooks, memory sizing in `confinit`, ISA-style config parsing, and case-insensitive string helpers.

Important behavior:
- Supports only one `Mach`.
- Memory sizing uses board constants `MEM1SIZE`, `MEM2SIZE`, and the end of kernel image.
- User/kernel page split depends on `*kernelpercent` and CPU-server mode.
- `init0` creates root/dot, initializes devices, starts `alarm` and `mmusweep`, then enters user mode through `touser`.
- `procsave` lazily saves FPU state only when active.

Dependencies:
- Relies on board-specific `machinit`, `trapinit`, `mmuinit`, `hwintrinit`, `timerinit`, `sharedseginit`, and UART console code.
- Depends on Plan 9 port layer process, segment, page, channel, and environment APIs.

Notable risks:
- `MAXCONF` is both the number of config entries and the temporary line buffer length, so long config lines are not supported.
- Boot ordering is strict: traps/MMU/memory/device setup are interdependent.
- `confinit` is Blast-board-specific despite living in generic PPC directory.
