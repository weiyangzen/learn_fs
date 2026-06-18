# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_trans.c

`tl_trans.c` implements the tableau-style translation from normalized LTL formula trees to an intermediate graph, then drives Büchi automaton generation.

Key responsibilities:
- Initializes graph translation state with `ini_trans`.
- Maintains graph-node sets, DFS stack, mapping table, red/green acceptance color counters, and generated state names.
- Builds acceptance/liveness obligations with `liveness`, `mk_grn`, and `mk_red`.
- Prints graph diagnostics with `dump_graph`, `sdump`, and `DoDump`.
- Emits PROMELA transition conditions with `dump_cond`, respecting `V_OPER`, `AND`, predicates, C expressions, optional `NEXT`, and condition elision.
- Computes Choueka-style red acceptance cycling with `choueka` and state-name prefixes with `set_prefix`.
- Converts graph nodes to FSM transitions with `fsm_trans` and finalizes via `mkbuchi`.
- Manages incoming/outgoing symbol sets with `dupSlist`, `catSlist`, and `Addout`.
- Normalizes graph formula sets with `flatten`, `Duplicate`, and `not_new`.
- Expands tableau graph nodes in `expand_g`, processing `AND`, `OR`, `U`, `V`, optional `NEXT`, predicates, and constants.
- Applies special two-case simplifications in `twocases`.
- Main `trans` rewrites/fixes the initial formula, expands the graph, computes liveness colors, builds the Büchi form, and prints it.

Important interactions:
- Receives formula tree from `tl_parse.c`.
- Calls `addtrans`/`fsm_print` in `tl_buchi.c`.
- Uses canonicalization/equality helpers from `tl_cache.c` and `tl_rewrt.c`.
- Uses `tl_out` for generated condition text.

Notable details:
- `Max_Red`, `Red_cnt`, and green/red color arrays implement acceptance-set tracking.
- `dump_cond` returns whether it printed no concrete condition, allowing callers to emit `1`.
