# File Research: sources/os/plan9/9front/sys/src/9/omap/io.h

OMAP I/O register definitions for GPMC and related low-level hardware.

Key contents:
- Timing and chip-select constants for the OMAP GPMC.
- `Gpmccs` chip-select register layout.
- `Gpmc` controller register layout, including config, IRQ, timeout, error, and per-chip-select register blocks.

Research notes:
- Used by architecture/flash-adjacent code that needs GPMC register-level access.
