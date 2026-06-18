# File Research: sources/os/plan9/9front/sys/src/9/pc/archgeneric.c

Fallback PC architecture implementation using legacy PIC and PIT hardware.

Key responsibilities:
- Provides `archreset()` using i8042 reset first, then Intel reset-control port `0xcf9`.
- Implements calibrated millisecond and microsecond delays through `delayloop`.
- Exposes low-overhead `perfticks()` backed by TSC when present.
- Defines the `archgeneric` `PCArch` vtable with i8259 interrupt and i8253 timer operations.

Important behavior:
- Writes BIOS warm-boot flag at `0x472` before attempting reset.
- Falls into `idle()` forever if reset does not work.
- Leaves architecture identification as nil so it acts as the default architecture.

Dependencies:
- Depends on i8042, i8259, i8253, TSC cycle helpers, and `PCArch` from `dat.h`.

Notable risks:
- Reset control port `0xcf9` is chipset-specific but used as a pragmatic final path.
