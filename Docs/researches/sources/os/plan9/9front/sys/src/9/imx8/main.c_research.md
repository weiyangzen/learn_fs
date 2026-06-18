# File Research: sources/os/plan9/9front/sys/src/9/imx8/main.c

Role: i.MX8 kernel entry orchestration, boot argument parsing, configuration, SMP bring-up, reboot, and DMA cache maintenance.

Key responsibilities:
- Parses `BOOTARGS`/plan9.ini-style text into `confname`/`confval`, stripping CR and mapping tabs to spaces.
- Exposes configuration through `getconf()`, `setconfenv()`, and `writeconf()`.
- Starts first user process in `init0()`, initializes devices/environment, starts alarm kproc, builds `boot` argv, exits FPU kernel state, and calls `touser()`.
- Computes memory/process/swap/image configuration in `confinit()`.
- Initializes per-CPU `Mach` state and active CPU bitmap.
- Starts secondary CPUs using PSCI `CPU_ON` SMC with MPID mapping and `_start` entry.
- Adds physical segments for TMU and ECSPI2, configuring pads/clocks for LPC SPI.
- `main()` handles separate secondary CPU path and primary boot path through memory, console, trap, FPU, interrupt, clock, page/proc/device/display/user/SMP/MMU/scheduler initialization.
- `exit()` powers off CPUs or system-resets CPU 0 through PSCI after clearing secrets.
- `reboot()` rewrites config, migrates to CPU 0, shuts devices/timer/interrupts, clears secrets, installs reboot trampoline, and jumps with identity map.
- `dmaflush()` performs clean/invalidate maintenance with `BLOCKALIGN` handling for DMA buffers.

Dependencies:
- Uses `rebootcode.i`, ARM64 SMC/sysreg support, Plan 9 core init functions, CCM/IOMUX, LCD, and memory/cache helpers.

Notes:
- `conf.nmach` defaults to `MAXMACH`.
- `dmaflush(clean=0)` preserves dirty partial cache lines around unaligned DMA receive ranges.
