# File Research: sources/os/plan9/9front/sys/src/cmd/1c/mul.c

Constant multiplication recipe table for the `1c` 68000 backend.

Key contents:
- Defines `multab[]`, mapping selected integer constants to compact character-coded instruction sequences.
- Sequence codes describe moves, adds, subtracts, and shifts between two scratch registers.
- Supports small constants and selected larger constants up to `9800`.
- Exposes `multabsize`.

Role in system:
- Used by `mulcon1` in `swt.c` and `cgen.c` to replace multiplication by constants with faster add/sub/shift sequences when profitable or available.

Notable details:
- The table assumes all generated sequences start from an initial copy unless the sequence begins with `i`, which suppresses the leading move.
