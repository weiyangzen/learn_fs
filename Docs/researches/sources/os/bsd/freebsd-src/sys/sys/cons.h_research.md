# File Research: sources/os/bsd/freebsd-src/sys/sys/cons.h

## Purpose
Defines the machine-independent console driver interface and kernel console entry points.

## Main Elements
- `struct consdev_ops` contains probe, init, term, getc, putc, grab, ungrab, and optional resume callbacks.
- `struct consdev` stores ops, priority, driver argument, capability flags, and console name.
- Console priorities: dead, low, normal, internal, remote.
- Flags: debugger-disabled and temporarily unavailable.
- `CONSOLE_DEVICE()` and `CONSOLE_DRIVER()` register console devices in the `cons_set` linker set.
- Kernel APIs include console init, add/remove/select, availability changes, grab/ungrab/resume, input polling/blocking, line input, output, constty attach/detach, and vty selection.

## Dependencies And Integration
Consumed by console drivers and implemented by `kern_cons.c`; integrates with tty redirection, message buffers, debugger paths, and `sc(4)`/`vt(4)` coexistence.

## Risk Notes
Console paths run during early boot and debugger/panic contexts. Driver callbacks must tolerate restricted locking and partial system initialization.
