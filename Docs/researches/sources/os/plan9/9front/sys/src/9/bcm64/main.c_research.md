# File Research: sources/os/plan9/9front/sys/src/9/bcm64/main.c

ARM64 BCM kernel entry, configuration, multiprocessor startup, and reboot handling.

Key responsibilities:
- Initializes first user process environment and enters `/boot/boot`.
- Computes memory allocation and kernel/user split.
- Initializes per-CPU `Mach` state.
- Wakes secondary CPUs through the spin table and events.
- Runs full kernel initialization sequence: bootargs, memory, pools, console, screen, traps, FPU, clocks, pages, processes, devices, user process, MMU, and scheduler.
- Sets ARM clock rate from firmware/config.
- Copies and invokes reboot trampoline with identity mapping restored.

Important behavior:
- Secondary CPUs take a shorter path into traps/FPU/clocks/MMU/scheduler.
- Sets `etherargs` from mailbox MAC address for boot networking.
- Uses `SPINTABLE` for ARM64 secondary boot coordination.

Dependencies:
- ARM64 MMU, mailbox/VideoCore helpers, platform arch hooks, scheduler, device/link initialization, and embedded reboot code.
