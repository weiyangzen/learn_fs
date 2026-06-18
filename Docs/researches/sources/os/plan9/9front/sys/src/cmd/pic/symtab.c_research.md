# File Research: sources/os/plan9/9front/sys/src/cmd/pic/symtab.c

`symtab.c` implements scoped symbol lookup for `pic` variables, places, definitions, and block-local names. `lookup()` searches from the current block stack outward. `makevar()` creates or updates a symbol in the current scope, while `getvar()` and `getfval()` retrieve union or numeric values with warnings for missing names.

It also provides `setfval()`, full symbol-table cleanup for blocks, and `freedef()` for removing macro definitions. The code assumes symbol names were allocated with `tostring()` when they need to be freed.
