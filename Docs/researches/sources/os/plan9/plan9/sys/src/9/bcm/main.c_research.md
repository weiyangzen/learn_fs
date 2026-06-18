# File Research: sources/os/plan9/plan9/sys/src/9/bcm/main.c

Main kernel entry, configuration parsing, first process creation, memory sizing, shutdown, and reboot handling for BCM.

Key behavior:
- Parses ATAGs and `plan9.ini`-style `name=value` configuration from `BOOTARGS`.
- Maintains early config arrays and exports `getconf()`/`addconf()`.
- `main()` clears BSS, initializes Mach/MMU/config, console/screen, firmware checks, traps, clock, timers, architecture reset, processes, segments, links, devices, pages, swap, first user process, and scheduler.
- Enforces minimum firmware revision `326770`.
- `init0()` sets root/dot, initializes devices, exports environment variables, starts alarm kproc, and enters user mode.
- `userinit()` creates the initial `*init*` process, stack segment with boot args, and text segment containing `initcode`.
- `confinit()` determines RAM size from VideoCore/ATAG/config, reserves kernel memory, sizes user pages, process count, swap, images, and pools.
- `exit()`/`shutdown()` coordinate kernel exit and call `archreboot()`.
- `reboot()` writes config, shuts down devices/clock/interrupts, copies reboot trampoline to `REBOOTADDR`, flushes caches, and jumps to physical reboot code.

It is the orchestration point for the BCM Plan 9 kernel lifecycle.
