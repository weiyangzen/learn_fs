# File Research: sources/os/plan9/9front/sys/src/9/pc/main.c

## Purpose
Defines the main PC kernel startup sequence, initial process entry, machine initialization, configuration sizing, process machine-state hooks, shutdown, and reboot path.

## Key Elements
`main()` performs ordered kernel initialization: Mach/boot args, traps, I/O, console/screen, CPU/memory/architecture setup, clock setup, RAM disk, configuration, allocators, PCI, MMU, interrupts, timers, process/channel/page/user initialization, and scheduler entry. `mach0init()` and `machinit()` initialize CPU 0 state. `init0()` initializes devices, sets environment variables, starts alarm kproc, builds the initial user stack, and calls `touser()`. `confinit()` sizes process/image/swap/kernel/user memory budgets. `procsetup()`, `procfork()`, `procrestore()`, and `procsave()` manage per-process GDT/LDT, debug registers, VMX, FPU, and TLB state. `exit()` and `reboot()` quiesce CPUs/devices, clear secrets, and jump through reboot trampoline code.

## Dependencies
Depends on nearly every early PC kernel subsystem: boot args, traps, I/O, console, CPU identify, memory, arch hooks, PCI, MMU, timers, process scheduler, channels, page allocator, FPU, VMX, pools, and reboot trampoline data.

## Behavior/Risks
Initialization order is critical. Reboot deliberately runs on CPU 0, disables devices, clears sensitive pages, resets secret pools, and remaps low memory before jumping to physical reboot code.
