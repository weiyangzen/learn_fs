# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/sym.c

Spin symbol-table and declaration bookkeeping module.

Key responsibilities:
- Maintains Promela symbols in `symtab[Nhash+1]` and insertion order in `all_names`.
- Implements scoped `lookup`, with legacy and newer scope behavior using `context`, `owner`, and `CurScope`.
- Performs declaration typing via `setptype`, including redeclaration checks, array-size validation, channel `Nid` assignment, hidden/show/local flags, and unsigned width validation.
- Tracks channel usage and exclusive receive/send claims through `setaccess`, `setxus`, `setonexu`, and `Xu_List`.
- Tracks `mtype` constants and maps names to values with `setmtype` and `ismtype`.
- Reports symbol tables, channel access, and unused variables through `symdump`, `symvar`, and `chanaccess`.

Important data flow:
- Parser-created `Lextok` name lists are typed here.
- Channel and variable metadata later drives verifier generation, warnings, and x[rs] safety claims.
- `trackrun` and `checkrun` inspect `run` statements to infer possible narrower parameter types.

Notable details:
- `disambiguate` rewrites non-global scoped names by prefixing scope bytes when modern scope rules are active.
- Hidden bit flags are overloaded for visibility, type-width hints, formal parameters, and use markers.
- `setmtype` enforces <=255 effective elements and assigns constant initializers.

Risks/quirks:
- Uses global mutable compiler state heavily.
- Scope comparison has subtle prefix matching under newer rules.
- Name rewriting intentionally leaks/abandons old name memory.
