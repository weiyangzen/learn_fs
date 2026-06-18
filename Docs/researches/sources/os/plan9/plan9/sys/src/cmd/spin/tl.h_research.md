# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl.h

Shared header for Spin's LTL translator.

Key responsibilities:
- Defines minimal `Symbol`, `Node`, `Graph`, and `Mapping` structures used by the LTL parser, rewriter, automaton generator, and Buchi printer.
- Defines token enum for temporal logic operators: `ALWAYS`, `EVENTUALLY`, `U_OPER`, `V_OPER`, `PREDICATE`, booleans, implication/equivalence, and optional `NEXT`.
- Declares cross-module APIs for parsing, lexing, canonicalization, graph translation, cache/memory management, and output.

Important data structures:
- `Node`: LTL AST with `ntyp`, `sym`, `lft`, `rgt`, and `nxt` list linkage.
- `Graph`: state-expansion node with New/Old/Next formula sets, incoming/outgoing symbols, acceptance color arrays, and reachability flags.
- `Mapping`: maps collapsed graph node names to canonical graph states.

Notable details:
- `Nhash` must match Spin's main `spin.h`.
- `rewrite(n)` macro applies right-linking and canonicalization.
- `True`, `False`, and `Not` are constructor macros that allocate AST nodes.

Risks/quirks:
- This header assumes C89-style global function declarations.
- `exit` is redeclared, reflecting old Plan 9/Spin portability style.
