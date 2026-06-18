# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.h

Shared declarations and core data structures for the `hoc` interpreter.

- Defines `Inst` as `void (*)(void)` and `STOP` as null instruction.
- Defines `Symbol`, `Symval`, `Datum`, `Saveval`, `Formal`, and `Fndefn`.
- `Symbol` supports variables, builtins, functions/procedures, strings, keywords, and undefined identifiers.
- `Datum` is the VM stack value union: numeric value or symbol pointer.
- Declares symbol-table, VM, parser, math, function-call, and execution helpers.

This header is the contract between parser (`hoc.y`), VM (`code.c`), builtins (`init.c`/`math.c`), and symbol table (`symbol.c`).
