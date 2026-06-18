# File Research: sources/os/plan9/plan9/sys/src/9/pc/devlml.c

Read completely: 403 lines.

This file implements a Plan 9 video device for LML/Zoran Motion JPEG capture hardware. It registers as the `video` device using rune `Λ`.

Key behavior:
- Probes PCI Zoran `36067` devices in `lmlreset()`.
- Allocates page-aligned `CodeData` buffers shared with hardware.
- Registers physical segments named `lmlN.mjpg` and `lmlN.regs`.
- Publishes per-card files: `lmlNctl`, `lmlNjpg`, and `lmlNraw`.
- Captured frame metadata is returned through reads of size `sizeof(FrameHeader)` or one byte for buffer number.
- Interrupt handler `lmlintr()` detects JPEG completion, updates embedded frame headers, and wakes readers.

Important interfaces:
- Depends on `devlml.h` for hardware structures and constants.
- Uses PCI mapping through `vmap()`, interrupt registration through `intrenable()`, and physical segment registration through `addphysseg()`.
- `lmlread()` on control files reports mapped register and MJPEG buffer physical locations.

Research notes:
- Only read opens are allowed, even for `lmlNctl`.
- `jpgopens` enforces one active capture stream per card.
- The raw and jpg file paths both use `jpgread()`, with raw using non-sleeping behavior.
