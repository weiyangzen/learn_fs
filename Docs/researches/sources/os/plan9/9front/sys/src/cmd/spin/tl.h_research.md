# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl.h

`tl.h` is the shared header for Spin's LTL-to-never-claim translator. It defines the LTL symbol table, formula AST, graph-state representation, token IDs, and function contracts for parsing, rewriting, caching, graph expansion, and Büchi printing.

Key definitions:
- `Symbol`: LTL symbol-table entry with name and hash-chain link.
- `Node`: LTL formula tree/list node with token type, symbol, left/right children, and list link.
- `Graph`: tableau graph node with name sets, formula sets (`New`, `Old`, `Other`, `Next`), red/green acceptance-color arrays, reachability, and next link.
- `Mapping`: maps symbolic names to graph nodes during translation.
- Token enum for LTL operators and leaves: `ALWAYS`, `AND`, `EQUIV`, `EVENTUALLY`, `FALSE`, `IMPLIES`, `NOT`, `OR`, `PREDICATE`, `TRUE`, `U_OPER`, `V_OPER`, optional `NEXT`, and `CEXPR`.
- Convenience macros: `True`, `False`, `Not`, `rewrite`, debug macros, and `Assert`.

Important interactions:
- `tl_parse.c`, `tl_lex.c`, `tl_cache.c`, `tl_rewrt.c`, `tl_trans.c`, `tl_buchi.c`, `tl_main.c`, and `tl_mem.c` all share this contract.
- It imports `emalloc` and `hash` from the broader Spin codebase, tying the TL translator to the main Spin runtime.
