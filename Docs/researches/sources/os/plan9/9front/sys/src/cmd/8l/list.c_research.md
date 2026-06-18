# File Research: sources/os/plan9/9front/sys/src/cmd/8l/list.c

Formatting and diagnostics support for the 386 linker `8l`.

Key contents:
- `listinit` installs Plan 9 `fmt` converters for registers, opcodes, addresses, short strings, and full `Prog` instructions.
- `Pconv` formats linker instructions, with special forms for `TEXT`, `GLOBL`, `DATA`, `INIT`, and `DYNT`.
- `Dconv` formats 386 operands: indirect registers, branches, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants.
- `Rconv` maps Plan 9 386 register/address enum values to textual register names, including x87, MMX, XMM, control/debug/task registers.
- `Sconv` escapes fixed-width string constants.
- `diag` reports linker errors in the current text symbol context, counts errors, and exits after too many unless debug `A` is set.

Filesystem relevance: indirect. This is build-tool listing/error infrastructure for 9front’s 386 linker, not filesystem logic.
