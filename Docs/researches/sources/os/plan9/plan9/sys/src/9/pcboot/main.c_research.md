# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/main.c

## Purpose
Main protected-mode bootstrap kernel entry and runtime setup for disk/PXE loading the next 386 or AMD64 kernel.

## Main Interfaces
- Exports `main`, `mach0init`, `machinit`, `init0`, `userinit`, `confinit`, `procsetup`, `procrestore`, `procsave`, `reboot`, `exit`, `isaconfig`, `cistrcmp`, `cistrncmp`, `idlehands`, and `trimnl`.
- Calls `bootloadproc` from the initial kernel process.

## Implementation Notes
- `main` enables A20, initializes Mach state, I/O, serial defaults, formatting, screen, traps, MMU, keyboard/timers, CPU ID, BIOS memory maps, memory config, architecture, process system, devices, pages, and scheduler.
- Detects missing PCI VGA and switches to serial-only screen output for headless Soekris-like systems.
- `init0` creates basic root/dot channels, initializes devices, starts alarm kproc, opens console, and enters `bootloadproc`.
- `userinit` creates a minimal kernel process with no user text/stack and schedules `init0`.
- `confinit` sizes bootstrap process/page/image/swap pools conservatively for loader use.
- `reboot` is inherited-style kernel reboot logic: moves to CPU0, shuts down other CPUs/devices, maps low memory, copies reboot trampoline, and jumps.

## Dependencies And Risks
- This is a reduced kernel runtime; many full-kernel paths are disabled or stubbed.
- Initialization ordering is critical: page initialization must follow memory and pool setup, and device loading happens after namespace/proc setup.
- `conf.npage` is forced from `MemMax`, not dynamically sized from all detected memory.
