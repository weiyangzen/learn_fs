# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlm78.c

Read completely: 346 lines.

This file implements the Plan 9 `#T` LM78 hardware monitor device. It exposes one file, `lm78vram`, backed by the LM78 value RAM registers `0x20..0x3f`.

Key behavior:
- Detects LM78 access through Intel PIIX/PIIX3 parallel port mapping or PIIX4 SMBus.
- `lm78reset()` probes PCI bridges and configures either `Parallel` or `Smbus` mode.
- `lm78enable()` verifies the chip address register and starts sampling without changing BIOS-configured interrupt/alarm masks.
- `lm78read()` reads byte ranges from value RAM.
- `lm78write()` can write value RAM offsets, despite the directory entry being mode `0444`.

Important interfaces:
- Device name: `lm78`, rune `'T'`.
- Files: `#T/lm78vram`.
- Uses `SMBus`, `piix4smbus()`, `pcimatch()`, `pcicfgr16()`, `pcicfgw16()`, `inb/outb`.

Research notes:
- Locking is centralized with `lm78` as a `QLock` around register access.
- SMBus reads are implemented as `SMBsend` followed by `SMBrecv`.
- The driver intentionally does not implement LM78 management interrupts.
