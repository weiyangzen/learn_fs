# File Research: sources/os/plan9/9front/sys/src/cmd/tl/optab.c

`optab.c` defines the ARM instruction selection table for `tl`.

Contents:
- `Optab optab[]` rows mapping:
  - opcode (`as`)
  - operand classes (`a1`, `a2`, `a3`)
  - emitter type number
  - emitted size
  - default base register parameter
  - flags such as `LFROM`, `LTO`, `LPOOL`, and `V4`

Coverage:
- Text pseudo-ops.
- ALU/register/immediate operations.
- Branch and branch-link forms.
- Loads/stores with small/large offsets.
- Byte/halfword moves and ARMv4 halfword ops.
- Floating-point loads/stores/arithmetic.
- Case/switch support.
- Relocatable address forms.
- Interworking forms `ABX` and `ABXRET`.

Integration:
- Consumed by opcode table builders and `oplook()`.
- `asmout()` interprets the `type` field to emit actual ARM words.

Risk notes:
- Table order matters for pattern matching.
- Sizes must match `asmout()` expansion exactly or phase errors and corrupted output can result.
