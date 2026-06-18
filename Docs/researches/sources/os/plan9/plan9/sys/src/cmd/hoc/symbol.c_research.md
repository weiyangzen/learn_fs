# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/symbol.c

Symbol-table and allocation helpers for `hoc`.

- Maintains a simple linked-list symbol table.
- `lookup()` linearly searches by symbol name.
- `install()` allocates a new `Symbol`, copies the name, sets type/value, and prepends to the table.
- `emalloc()` wraps `malloc` and reports out-of-memory through `execerror()`.
- `formallist()` builds linked formal-parameter lists for function/procedure definitions.

Notable concerns: symbol lookup is O(n), and installed symbols are never freed during normal interpreter lifetime.
