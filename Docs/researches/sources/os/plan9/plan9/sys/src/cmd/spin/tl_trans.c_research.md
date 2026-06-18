# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_trans.c

Core LTL-to-automaton translation module based on Gerth/Peled/Vardi/Wolper.

Key responsibilities:
- Expands LTL formulas into graph states using New/Old/Next formula sets.
- Collapses equivalent states via canonical Old/Next representations.
- Computes acceptance conditions for until formulas.
- Converts the Streett-like intermediate graph into Buchi transitions emitted by `tl_buchi.c`.

Important functions:
- `expand_g`: main state-expansion algorithm for AND, OR, U, V, predicates, booleans, and optional NEXT.
- `not_new`: detects duplicate graph states and records mappings.
- `fixinit`: creates explicit init graph and resolves incoming/outgoing edges.
- `liveness`, `mk_red`, `mk_grn`: classify states for acceptance obligations.
- `mkbuchi`/`fsm_trans`: generate named Buchi states and transitions.
- `dump_cond`: emits transition guard expressions.
- `trans`: top-level translation driver.

Data structures:
- `Nodes_Stack`: pending graph states.
- `Nodes_Set`: accepted graph states.
- `Mapped`: collapsed name mapping.
- Acceptance labels use fixed `isred[64]` and `isgrn[64]` arrays in `Graph`.

Risks/quirks:
- Fatal if more than 63 until acceptance classes.
- Uses name strings to identify graph nodes and mappings.
- Extensive mutable list manipulation across `nxt`, `lft`, and `rgt`.
