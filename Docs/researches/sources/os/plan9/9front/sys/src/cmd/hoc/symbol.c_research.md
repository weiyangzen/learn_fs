# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/symbol.c

Implements the `hoc` symbol table, checked allocation, and formal-parameter list construction.

Key points:
- Maintains a simple linked-list symbol table.
- `lookup` scans for an exact name match.
- `install` allocates a `Symbol`, copies the name, sets type/value, and prepends it to the list.
- `emalloc` wraps `malloc` and raises `execerror` on allocation failure.
- `formallist` prepends a formal parameter to a formal list and initializes its saved-value stack.

Dependencies and interactions:
- Used by `hoc.y`, `init.c`, and `code.c`.
- Relies on `execerror` for fatal allocation handling.

Research relevance:
- This is the interpreter’s name storage layer and formal-parameter data structure support.
