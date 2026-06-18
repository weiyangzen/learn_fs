# File Research: sources/teaching/xv6-public/asm.h

Assembler helper header for x86 segment descriptor setup.

Defines:
- `SEG_NULLASM` for a null GDT entry.
- `SEG_ASM(type, base, lim)` for emitting a flat x86 segment descriptor in assembly.
- Segment access bits `STA_X`, `STA_W`, and `STA_R`.

Used by boot and entry assembly files to construct temporary GDTs before the C kernel initializes per-CPU descriptors.
