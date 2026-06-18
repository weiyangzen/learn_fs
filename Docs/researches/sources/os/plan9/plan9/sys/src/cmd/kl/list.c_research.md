# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/list.c

Read fully: 258 lines, 4502 bytes. SHA-256 prefix: `c64a84e2e8647b3a`.

This file installs and implements Plan 9 `Fmt` printers for linker diagnostics and assembly listings. `listinit()` registers `%A`, `%D`, `%P`, `%S`, and `%N`. `prasm()` prints a single `Prog`.

The converters format:
- `Pconv()`: complete instruction, including data pseudo-ops, explicit registers, special memory forms, and NOSCHED marker.
- `Aconv()`: opcode name via `anames`.
- `Dconv()`: operand by type, including registers, constants, branches, strings, IEEE constants, and offset/address forms.
- `Nconv()`: symbol-qualified names for extern, static, auto, and parameter addressing.
- `Sconv()`: string constants with C-style escapes.
- `diag()`: emits errors with current text symbol context and aborts after too many errors.

Integration: diagnostics throughout the linker use these formatters, especially illegal instruction combinations, bad object records, and debug listings.

Risk notes: `Pconv()` assigns `curp = p`, so formatting has side effects used by branch operand formatting.
