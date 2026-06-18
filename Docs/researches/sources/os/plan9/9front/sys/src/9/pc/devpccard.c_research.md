# File Research: sources/os/plan9/9front/sys/src/9/pc/devpccard.c

CardBus and 16-bit PC Card bridge driver implementing `#Y` and replacing/competing with older PCMCIA hooks.

Key responsibilities:
- Detects supported PCI/CardBus bridge variants from Ricoh, TI, and O2Micro.
- Maps CardBus socket registers, initializes bridge windows, bus numbers, interrupts, and vendor-specific bridge quirks.
- Maintains a slot state machine for card detected, powered, ejected, and configured events.
- Queues interrupt-driven card events to a kernel process for serialized power/configuration handling.
- Powers PC16 and PC32 cards, configures PC32 CardBus PCI devices, allocates bridge I/O and memory windows, maps child BARs, and assigns interrupts.
- Parses PC16 CIS tuples for version strings, configuration address/present bits, power, timing, I/O ranges, IRQ masks, and memory descriptions.
- Provides `pcmspecial` hooks for ISA-style drivers to claim matching PC16 cards and program PCIC-compatible I/O/IRQ windows.
- Exposes `cbNctl` files showing slot state, child PCI devices, PC16 configuration tables, and accepting `down`/`power` controls.

Important behavior:
- Uses a shared legacy PCIC index/data pair at `0x3e0/0x3e1` for 16-bit card compatibility.
- For PC32 cards, sizes downstream PCI resources, reserves at least 512 bytes I/O and 1 MiB memory, then programs CardBus bridge window registers.
- For PC16 cards, uses 4 KiB ISA memory mapping granularity and PCIC register programming similar to `devi82365.c`.
- `down` control can call a named device's config hook before forcing a CardEjected event.

Dependencies:
- Depends on PCI bridge scanning/sizing/mapping/freeing, I/O and upper-physical memory allocators, PCMCIA CIS structures, `_pcmspecial` hooks, interrupts, and device framework.

Notable risks:
- Event queue is fixed at ten entries and drops excess events.
- PC16 unconfiguration is incomplete beyond clearing in-memory info.
- Vendor setup uses several bridge-specific magic register writes.
