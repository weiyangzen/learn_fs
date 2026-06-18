# File Research: sources/os/plan9/9front/sys/src/9/teg2/main.c

Tegra 2 kernel bootstrap, configuration, memory sizing, and reboot path.

Purpose:
- Orchestrates CPU0 initialization after `l.s` reaches C.
- Parses early `plan9.ini` data from `CONFADDR`.
- Initializes caches, MMU, traps, memory pools, devices, PCI, processes, and secondary CPUs.

Key behavior:
- `plan9iniinit`, `getconf`, `addconf`, and `writeconf` manage boot configuration.
- `mach0init`, `machinit`, `launchinit`, `machon`, and `machoff` manage per-CPU `Mach` state.
- `main` performs ordered boot: BSS clear, SMP/cache setup, console, MMU, config, trap, memory, devices, page allocator, user process, secondary CPU startup, scheduler.
- `confinit` probes memory, computes page/process/image/swap sizing, and sets copy-on-reference mode.
- `reboot` shuts down devices, copies `rebootcode` to `REBOOTADDR`, disables caches through the trampoline, and jumps to the next kernel.

Filesystem relevance:
- Initializes channel devices, page allocator, process environment, and storage-visible PCI/device layers before filesystems/userspace can run.

Risks/notes:
- Boot order is fragile: traps must exist before memory probing; locks need SMP/cache setup; malloc availability is called out explicitly.
- Memory sizing assumes 1 GiB DRAM and reserved high-memory regions.
