# File Research: sources/os/plan9/9front/sys/src/9/kw/trap.c

Kirkwood ARM trap, fault, and interrupt handling. It defines handler tables for low, high, and bridge interrupt banks, installs vectors/stacks, dispatches interrupts, handles ARM fault status codes, and provides debug register/stack dump helpers.

`trapinit` maps vector code into `HVECTORS`, initializes banked stacks, disables/clears interrupt sources, registers high/bridge summary handlers, and enables watchdog/access-error bridge interrupts. `intrenable`/`intrdisable` attach one handler per interrupt bit and update masks.

`trap` handles IRQs, prefetch aborts, data aborts, and undefined instructions. Data aborts inspect FSR/FAR and decide between VM fault handling, user notes, or kernel panic. Undefined user instructions are passed to ARM floating-point emulation before posting a debug note.

The file also supports interrupt timing histograms, probing fault-prone addresses, stack traces, and register dumps.

Notable risks: interrupt registration silently ignores duplicate handlers; fault probing uses global state and a lock; trap behavior depends on exact PC correction for abort types.
