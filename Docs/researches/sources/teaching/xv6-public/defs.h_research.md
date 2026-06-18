# File Research: sources/teaching/xv6-public/defs.h

Central kernel function declaration header.

Contents:
- Forward declarations for core kernel structs.
- Prototypes grouped by implementation file: buffer cache, console, exec, files, filesystem, IDE, APICs, allocator, keyboard, log, MP, PIC, pipes, process scheduler, locks, strings, syscalls, traps, UART, and VM.
- External globals such as `ticks`, `tickslock`, `lapic`, and `ioapicid`.
- `NELEM(x)` array-length macro.

Role:
- Provides compile-time coupling across xv6’s simple non-modular kernel.
- Documents major subsystem boundaries in one place.
