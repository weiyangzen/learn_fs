# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevherc.c

Direct Hercules Graphics Card framebuffer display driver for DOS-era PC hardware.

Key behavior:
- Defines `herc` display at 720x350 mono.
- Programs Hercules CRTC/registers directly and clears video memory at `0xb0000000L`.
- Implements fill rectangle, mono copy, and color copy using far framebuffer pointers and Hercules interleaved memory layout.
- Saves/restores previous BIOS video mode.

Risks / notes:
- Highly hardware-specific and non-portable.
- Direct port I/O and far pointers assume 16-bit x86 DOS memory model.
- Several loops use inclusive bounds after clipping; behavior depends on historical helper macros.
