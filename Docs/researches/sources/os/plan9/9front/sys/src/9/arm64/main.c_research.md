# File Research: sources/os/plan9/9front/sys/src/9/arm64/main.c

ARM64 kernel mainline, CPU startup, reboot, exit, and DMA cache flush handling.

Key behavior:
- `init0` initializes devices/environment, starts alarm process, builds initial user stack, and enters user mode.
- `confinit` computes CPU count, process counts, page pools, swap/image sizing, and kernel memory pool limits.
- `main` initializes console, boot arguments, memory, traps, FPU, interrupts, clock, pages, processes, devices, and scheduler.
- Secondary CPUs initialize traps/FPU/interrupts/clock/MMU and enter scheduler.
- `mpinit` starts other CPUs through PSCI `CPU_ON` hypercalls.
- `exit` uses PSCI CPU off or system reset.
- `reboot` serializes config, shuts down devices/clock/interrupts, clears secrets, and jumps through reboot trampoline.
- `dmaflush` performs clean/invalidate with block alignment.

Dependencies:
- Uses broad kernel port APIs, PSCI `hvccall`, `rebootcode`, cache operations, and memory/pool subsystems.

Research notes:
- The port assumes QEMU-like CPU identification and reset behavior.
- Reboot explicitly returns to an identity-mapped trampoline.
