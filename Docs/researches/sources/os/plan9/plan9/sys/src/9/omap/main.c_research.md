# File Research: sources/os/plan9/plan9/sys/src/9/omap/main.c

OMAP kernel mainline and early system initialization for Plan 9.

Key responsibilities:
- Parses and stores boot arguments and `plan9.ini` configuration from `CONFADDR`.
- Initializes `Mach`, MMU, traps, memory sizing, pools, clocks, screen, devices, paging, swap, and the first user process.
- Provides configuration lookup/update helpers: `getconf`, `addconf`, `isaconfig`, `getenv`, and `writeconf`.
- Implements shutdown, `exit`, and in-memory kernel reboot through `rebootcode`.
- Creates the initial process, stack, argument vector, and `initcode` text mapping.
- Computes `Conf` memory/process/page/swap/image sizing.
- Probes physical memory size by temporarily identity-mapping candidate addresses and using `probeaddr()`.

Important behavior:
- Starts with conservative 256 MiB default memory, accepts `*maxmem`, and probes 256/128 MiB fallbacks.
- Clears BSS and verifies possible data-segment realignment after bootloader load quirks.
- Converts `plan9.ini` variables into both volatile and configuration environment entries in `init0`.
- Uses `touser(sp)` to enter the initial user process.
- Reboot copies trampoline code to `REBOOTADDR`, shuts down devices/clocks/interrupts, then calls it with physical addresses.

Dependencies:
- Depends on port kernel initialization routines, OMAP MMU/trap routines, `initcode`, `rebootcode`, pool allocator, device reset/init hooks, and ARM process entry assembly.

Notable risks:
- Many initialization calls have strict ordering comments, especially trap setup before memory probing and malloc/pool initialization before print/device paths.
- `getenv` searches only the local `oenv` buffer, which is initially empty except for any prior boot-argument population.
- `bootargs` notes its stack layout is not strictly the conventional argc/argv ABI but works with Plan 9 `startboot`.
