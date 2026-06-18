# File Research: sources/os/plan9/9front/sys/src/cmd/1l/list.c

Listing, formatting, and diagnostics support for `1l`.

Key responsibilities:
- Installs formatters for registers, opcodes, addresses, strings, and programs.
- `Pconv` prints instructions with line number and operands, including bitfield suffixes.
- `Dconv` formats linker `Adr` values, including resolved branch targets, extern/static/auto/param, constants, quick constants, float/string constants, and indirect addressing forms.
- `Rconv` formats data, address, FP, and special registers.
- `Sconv` escapes fixed-size string constants.
- `diag` reports errors prefixed by current function text symbol and aborts after too many errors.

Notable details:
- `D_BRANCH` printing uses `bigP->pcond->pc` when available, so debug output reflects resolved branch targets.
