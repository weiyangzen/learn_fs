# File Research: sources/os/bsd/netbsd-src/sys/sys/kgdb.h

Defines the KGDB remote serial debugging protocol constants and kernel stub interface. It names GDB remote packet operations, frame markers, acknowledgment bytes, exported KGDB state variables, attach/connect/panic/trap routines, and MD hooks for signal mapping, memory access validation, register transfer, and entry notification.

The header connects DDB, machine register definitions, and serial remote debugging. Risks are machine-dependent register format compatibility and trap recovery safety while the kernel is already faulting or panicking.
