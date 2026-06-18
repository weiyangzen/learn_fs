# File Research: sources/os/plan9/9front/sys/src/9/sgi/main.c

SGI kernel bootstrap and machine setup. `main` initializes ARCS console, memory, `conf`, `Mach`, kmap, timers, formats, optional graphics, TLB, pages, processes, devices, first user process, and scheduler.

Memory discovery reads SGI memory config registers and filters out kernel and ARCS-reserved regions. `machinit` installs ARCS-dispatched exception hooks for UTLB miss and general exceptions, clears FP interrupts, and initializes the clock. `init0` sets environment variables and starts `boot`.

Also handles process FP state setup/fork/save, reboot through ARCS, kernel config sizing, and basic stubs for watchpoints/ISA config.
