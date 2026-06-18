# File Research: sources/os/plan9/9front/sys/src/cmd/5l/list.c

This file implements formatting and diagnostics for `5l` internal instructions and operands.

Key elements:
- `listinit()` installs custom formatters `%A`, `%C`, `%D`, `%P`, `%S`, and `%N`.
- `Pconv()` prints a `Prog` in assembly-like form, handling special forms such as `SWP`, `DATA`, `INIT`, and `DYNT`.
- `Aconv()` maps opcode numbers to names via `anames[]`.
- `Cconv()` formats ARM condition/suffix bits such as `.EQ`, `.S`, `.P`, `.W`, and `.U`.
- `Dconv()` formats operand types: constants, shifts, memory operands, registers, register pairs, F registers, PSR/FPCR, branches, floating constants, and string constants.
- `Nconv()` formats symbol-relative names for extern, static, auto, and parameter operands.
- `Sconv()` escapes string constants.
- `diag()` prints contextual linker diagnostics and aborts after more than 10 errors.

Dependencies and integration:
- Uses globals `curp`, `curtext`, `nerrors`, and `noname`.
- Called by most linker passes for debugging and error reporting.

Notable behavior:
- Branch formatting uses `curp->cond->pc` when branch target has been resolved.
- Versioned symbols are printed using Plan 9 linker conventions.
- `diag()` prefixes messages with current text symbol where available.

Research notes:
- This file is essential for readable linker debug output and error messages, not for output binary semantics.
