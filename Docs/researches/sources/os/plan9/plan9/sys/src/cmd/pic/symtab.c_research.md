# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/symtab.c

Symbol-table support for the Plan 9 `pic` preprocessor.

Key responsibilities:
- Looks up variables/place names across the active block stack.
- Gets and sets numeric variable values stored in `YYSTYPE`.
- Creates or updates symbols in the current stack frame.
- Frees entire symbol tables and individual macro definitions.

Important behavior:
- `lookup()` searches from innermost stack frame down to global scope.
- `makevar()` assumes names are static or allocated by `tostring()`, then stores the pointer directly.
- `freedef()` only removes symbols of type `DEFNAME`.

Dependencies:
- Uses `pic.h`, `y.tab.h`, parser globals `stack` and `nstack`, and `ERROR` diagnostics.

Notable risks:
- Ownership is implicit: `freesymtab()` always frees `s_name`, so callers must not pass unowned transient strings.
- `getvar()` returns a static zero-ish fallback after warning, which can hide missing variable errors.
