# File Research: sources/os/plan9/9front/sys/src/cmd/db/regs.c

Purpose: Register lookup, read/write, and printing for `db`.

Key behavior:
- `rname()` finds a register in `mach->reglist`.
- `getreg()` reads register values from a map according to register format: 16-bit, 32-bit, or 64-bit.
- `rget()` resolves a register name and returns its value.
- `rput()` writes a register unless marked read-only.
- `printregs()` prints integer registers in rows and, with `R`, includes floating registers except special unsupported formats; then prints exception text and current pc.

Notable details:
- Register offsets are “magic” offsets understood by the active machine/map backend.
- Errors are reported through `error("%r")`.
