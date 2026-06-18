# File Research: sources/os/plan9/plan9/sys/src/9/rb/initreboot.s

Minimal MIPS assembly helper for reboot/runtime entry on RouterBOARD.

Key responsibilities:
- `_main` sets `R30` and jumps directly to C `main`.
- Defines `ret` target used by barrier macros.
- Provides `setsp`, `coherence`, and full I/D cache clean/invalidate helper `cleancache`.

Role:
- Small standalone low-level support for reboot or reduced initialization contexts.

Dependencies:
- Includes `mem.h` and `mips.s`; uses MIPS cache/barrier macros.

Notable risks:
- Cache flush operates by index over fixed cache-size constants.
- Interrupt state is changed during cache cleaning and restored afterward.
