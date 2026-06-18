# File Research: sources/os/plan9/9front/sys/src/cmd/tl/list.c

`list.c` provides formatting and diagnostics for linker internal instructions and operands.

Functions:
- `listinit()` installs formatters `%A`, `%C`, `%D`, `%P`, `%S`, and `%N`.
- `prasm()` prints a `Prog`.
- `Pconv()` formats full instructions.
- `Aconv()` formats opcodes through `anames`.
- `Cconv()` formats ARM condition suffixes and condition bits.
- `Dconv()` formats operands by `Adr.type`.
- `Nconv()` formats symbol/name addressing modes.
- `Sconv()` escapes string constants.
- `diag()` prints an error in current text context and aborts after too many errors.

Integration:
- Used throughout `tl` debug output and diagnostics.
- Depends on `curp`, `curtext`, `anames`, and IEEE conversion helpers.

Risk notes:
- Diagnostic count threshold is 10 before `errorexit()`.
- Formatting relies on global `curp` for branch target display.
