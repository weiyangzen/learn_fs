# File Research: sources/os/plan9/plan9/sys/src/9/pc/devpccard.c

Read completely: 1920 lines.

This file implements Plan 9 CardBus and 16-bit PCMCIA support, exposed as device `#Y` named `cardbus`.

Key behavior:
- Detects supported CardBus bridges from TI, Ricoh, and O2Micro.
- Maintains up to four slots in `cbslots`.
- Uses a state machine for `SlotEmpty`, `SlotFull`, `SlotPowered`, and `SlotConfigured`.
- Handles events: card detected, powered, ejected, and configured.
- CardBus PCI cards are scanned as subordinate PCI buses and assigned memory/I/O windows.
- 16-bit PCMCIA cards use legacy i82365-compatible registers, CIS parsing, memory windows, I/O windows, IRQ routing, and config-register writes.
- Exposes per-slot control files `cbNctl`.

Important interfaces:
- Device name: `cardbus`, rune `'Y'`.
- Files: `#Y/cbNctl`.
- Installs global hooks `_pcmspecial` and `_pcmspecialclose` so legacy drivers can claim PCMCIA cards by version string.
- Uses PCI bridge config registers, socket event/status registers, and legacy index/data ports at `0x3e0/0x3e1`.

Key internal pieces:
- `devpccardlink()` discovers bridges, maps controller registers, initializes interrupts, and starts card detection.
- `configure()` handles 32-bit CardBus PCI resource allocation.
- `i82365configure()` maps attribute memory and parses CIS tuples.
- `pccard_pcmspecial()` selects a matching 16-bit card, configures I/O ranges, IRQ, voltage, and optional config-register index.
- CIS tuple handlers include `tvers1`, `tcfig`, and `tentry`.

Research notes:
- The file combines kernel device namespace code, PCI bridge management, PCMCIA CIS decoding, and legacy card allocation.
- `pccardwrite()` supports `down <device>` and `power`.
- Some paths are explicitly incomplete, including PC16 unconfigure and memory-region file entries.
