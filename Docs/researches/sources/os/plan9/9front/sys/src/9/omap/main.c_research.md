# File Research: sources/os/plan9/9front/sys/src/9/omap/main.c

Main OMAP kernel bootstrap and machine configuration.

Key behavior:
- Maintains parsed configuration entries from `plan9.ini` via `getconf`, `addconf`, `writeconf`, and `plan9iniinit`.
- `main` sequences early initialization: machine setup, UART, architecture reset, trap/MMU/process subsystems, devices, links, environment, clock, screen, and first user process.
- `machinit` initializes the single `Mach` structure and per-mode stacks.
- `reboot` copies reboot trampoline code to `REBOOTADDR`, shuts down devices/clocks/interrupts, and calls the trampoline.
- `init0` completes first-process setup and enters user space.
- `confinit` detects available DRAM by probing possible memory sizes, builds `Conf.mem`, computes page/proc/swap/image allocation sizes, and sets uniprocessor config.
- `isaconfig` parses ISA-style config strings.
- `cmpswap` maps to ARM CAS.
- `setupwatchpts` reports unsupported watchpoints.

Research notes:
- Memory probing relies on `trapinit`/`probeaddr` being ready.
- The port assumes one CPU and uses an OMAP-specific base DRAM map.
