# File Research: sources/os/plan9/9front/sys/src/9/kw/main.c

Kirkwood kernel C entry and platform bring-up. It parses early `plan9.ini` from `CONFADDR`, manages configuration variables, initializes Mach state, memory configuration, devices, processes, and the first user process.

`main` is called after assembly has enabled the MMU. It handles possible data-segment realignment, zeros BSS, initializes console UART, machine state, architecture reset, MMU, traps, clock, printing, memory, devices, user process, and scheduler.

Reboot support serializes the current configuration back into boot args, shuts down devices/clocks, clears secret memory, copies `rebootcode` to `REBOOTADDR`, flushes caches, and jumps into the trampoline with physical entry/code/size.

`confinit` hard-codes Sheeva memory as 512 MiB minus an 8 KiB reservation, excludes kernel pages, and sizes process, swap, image, interrupt, and memory pools.

Notable risks: memory sizing is static for the platform; comments warn data segment misalignment can fail late; `writeconf` must fit in the fixed boot-args area.
