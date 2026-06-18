# File Research: sources/os/bsd/freebsd-src/sys/sys/reboot.h

Read completely: 70 lines.

## Purpose
Defines reboot/boot flags passed through reboot paths, boot programs, and init.

## Main Elements
- Defines `RB_AUTOBOOT` and flags for asking root name, single-user boot, no sync, halt, default root, debugger, read-only root, crash dump, verbose boot, serial/CD-ROM console/root options, poweroff, GDB, muted console, pause, reroot, powercycle, kexec, console probing, multiple consoles, and bootinfo argument presence.
- Includes reserved/unused placeholders for compatibility.

## Dependencies And Integration
Used by kernel reboot/shutdown paths, boot loader/boot blocks, init behavior, console selection, dump handling, and root filesystem behavior.

## Risk Notes
Flag values are cross-component ABI. Reserved and unused values should not be casually repurposed because boot components may pass them through.
