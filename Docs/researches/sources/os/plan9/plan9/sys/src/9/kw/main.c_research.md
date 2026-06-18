# File Research: sources/os/plan9/plan9/sys/src/9/kw/main.c

## Role

Kirkwood kernel C entry and board initialization. It parses boot configuration, initializes CPU/MMU/traps/devices, creates the first user process, configures memory, and implements reboot/shutdown support.

This is OS/platform bring-up. It indirectly supports filesystems by initializing device and memory infrastructure.

## Main Interfaces

- Kernel entry and setup:
  - `main(Mach *mach)`
  - `machinit`
  - `cpuidprint`
  - `confinit`
  - `userinit`
  - `init0`
- Boot configuration:
  - `getconf`
  - `addconf`
  - `getenv`
  - `plan9iniinit`
  - `optionsinit`
  - `bootargs`
- Shutdown/reboot:
  - `exit`
  - `reboot`
- Utility:
  - `cmpswap`
  - `spiprobe`
  - `probeaddr` is declared and used for probing memory.

## Important Behavior

- Reads boot arguments from `CONFADDR` into a parsed `confname`/`confval` table.
- Initializes UART console early, MMU, traps, clocks, links, page allocator, process subsystem, and device roots.
- Builds and starts the initial user process using `initcode`.
- `confinit` determines memory size using configured `memsize` or probing.
- `reboot` copies reboot code to low memory, turns off interrupts/caches, and jumps to supplied entry code.
- `spiprobe` reads SPI flash register bytes for diagnostic output.

## Dependencies And Assumptions

- Includes `init.h`, `arm.h`, `io.h`, `tos.h`, and pool definitions.
- Assumes Kirkwood memory layout from `mem.h`.
- Assumes one CPU (`MAXMACH` is 1 in `mem.h`).

## Notable Risks

- Boot configuration parsing is small and fixed-size (`MAXCONF`, `MAXCONFLINE`).
- Memory probing and reboot code operate near raw physical addresses.
- Early console and panic paths depend on hardware UART availability.
