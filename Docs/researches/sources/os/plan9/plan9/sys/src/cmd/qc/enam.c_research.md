# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/enam.c

Purpose: Provides architecture instruction name strings for the PowerPC compiler/assembler toolchain.

Key contents:
- `anames[]` maps opcode enum indexes to printable mnemonics.
- Covers base integer, branch, compare, floating-point, move, condition-register, special, pseudo, embedded MAC, optional 32-bit floating, fp2, and final `LAST` entries.

Dependencies and integration:
- Referenced through `extern char *anames[]` in `gc.h`.
- Used by listing/formatting/debug output.

Risks and notes:
- Must stay exactly synchronized with opcode enum values in `q.out.h`.
- Pure data table; no control flow.
