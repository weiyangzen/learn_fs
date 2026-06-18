# File Research: sources/os/plan9/plan9/sys/src/cmd/db/regs.c

This file manages debugger register lookup, reading, writing, and formatted register display.

Key behaviors:
- `rname()` resolves a register name against `mach->reglist`.
- `getreg()` reads a register from a `Map` using register format metadata:
  - `'x'`: 2-byte value.
  - `'f'`, `'X'`: 4-byte value.
  - `'F'`, `'W'`, `'Y'`: 8-byte value.
- `rget()` reads a named register.
- `rput()` writes a named register unless marked read-only.
- `printregs()` prints integer registers by default and floating-point registers only for `$R`, then prints machine exception text and current PC.

Notable implementation details:
- Error messages include the register name when a map read fails.
- `printregs()` formats 64-bit `'Y'` registers wider than ordinary registers.
- Floating register display skips some register formats for normal `$r` output.
