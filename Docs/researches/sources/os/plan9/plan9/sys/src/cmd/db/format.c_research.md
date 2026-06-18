# File Research: sources/os/plan9/plan9/sys/src/cmd/db/format.c

Format-string executor for Plan 9 `db` examine commands.

Key responsibilities:
- `scanform()` repeats a full format string for a count, preserving and incrementing `dot`.
- `exform()` executes one format item `fcount` times and advances `dot`.
- Supports address/symbol output formats:
  - `a`, `A`, `p`.
- Supports numeric formats:
  - 16-bit `u d x o q`
  - 32-bit `U D X O Q`
  - 64-bit `Z V Y`.
- Supports byte/char/rune/string formats:
  - `B b c C r R s S`.
- Supports disassembly/instruction formats:
  - `i`, `I`, `M`.
- Supports float formats:
  - `f`, `F`.
- Supports spacing/control:
  - spaces/tabs, `t`, `T`, `n`, `N`, quoted strings, `^`, `+`, `-`, `z`.
- `printesc()` prints escaped non-printable chars.
- `inkdot()` increments `dot` with wraparound detection.

Important interactions:
- Uses `machdata` hooks for disassembly and floating formatting.
- Uses `get1`, `get2`, `get4`, `get8` for memory reads from `Map`.
- Uses `symoff`, `findsym`, and `printsource`.

Research notes:
- On the first pass, instruction formats warn if `dot` is not aligned to `mach->pcquant`.
- Literal mode treats `dot` as the value rather than reading from a map.
- Comments note `f` and `F` literal cases assume `szdouble` fits in a `vlong`.
