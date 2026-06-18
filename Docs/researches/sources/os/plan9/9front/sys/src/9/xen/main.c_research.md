# File Research: sources/os/plan9/9front/sys/src/9/xen/main.c

Main bootstrap and configuration for the Xen x86 Plan 9 kernel.

Purpose:
- Initializes the Plan 9 kernel as a Xen guest.

Key behavior:
- `options` parses Xen `start_info.cmd_line` as `plan9.ini`-style key/value lines.
- `main` initializes Mach state, Xen console, CPU, config, architecture, clock, allocator, traps, MMU, timers, FPU, keyboard/console, grant table, processes, devices, page allocator, first user process, and scheduler.
- `mach0init` and `machinit` set CPU0 Mach/PDB and map Xen shared info.
- `confinit` sizes usable memory below the hypervisor virtual window and sets process/image/swap/pool limits.
- Process hooks delegate to FPU helpers and flush TLB on save.
- `reboot` handles Xen shutdown for `entry == 0` or copies reboot trampoline for kernel restart.

Filesystem relevance:
- Initializes xenstore, virtual block/network devices, channel devices, page cache backing memory, and user boot environment.

Risks/notes:
- Memory above Xen’s mappable virtual boundary is ignored with a warning.
- Several boot comments reflect old PC assumptions adapted to Xen.
