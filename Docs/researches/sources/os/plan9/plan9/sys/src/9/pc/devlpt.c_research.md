# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlpt.c

Read completely: 241 lines.

This file implements the Plan 9 Centronics parallel printer port device `#L`.

Key behavior:
- Supports three base addresses: `0x378`, `0x3bc`, and `0x278`.
- Attaching `#L` optionally selects a printer number.
- Exposes per-port files generated as `lptNdlr`, `lptNpsr`, `lptNpcr`, and `lptNdata`.
- `dlr`, `psr`, and `pcr` map to hardware registers.
- Writes to `data` send bytes using strobe control and wait for printer readiness.
- Interrupt handler wakes sleepers waiting for `Fnotbusy`.

Important interfaces:
- Device name: `lpt`, rune `'L'`.
- Uses `ioalloc()`, `intrenable(IrqLPT, ...)`, `inb/outb`, and `Rendez`.

Research notes:
- ECP ports are detected through the extended control register and forced toward PS/2-compatible mode when possible.
- `lptgen()` encodes hardware register addresses directly into Qid paths for non-data entries.
