# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/utils.c

Role: Flashfs global variables and small binary encoding helpers.

Globals:
- Defines `prog`, sector geometry, sector buffer, readonly flag, clock delta, active parity, and magic bytes.

Helpers:
- `putc3` encodes unsigned values into 1 to 3 bytes using continuation bits, supporting up to 21 bits.
- `getc3` decodes that compact integer form.
- `get4` and `put4` read/write little-endian 32-bit values.

Failure behavior:
- `putc3` prints diagnostics and aborts if a value does not fit in 21 bits.
