# File Research: sources/os/plan9/9front/sys/src/cmd/spin/tl_buchi.c

`tl_buchi.c` converts the intermediate LTL translation graph into a minimized PROMELA `never` claim. It owns the printable Büchi-state/transition representation and post-translation cleanup.

Key responsibilities:
- Defines `State` and `Transition` lists separate from the tableau `Graph`.
- Initializes module state with `ini_buchi`.
- Adds graph transitions with `addtrans`, pruning and rewriting transition conditions before storing them.
- Prunes non-condition formula nodes with `Prune`.
- Retargets transitions and marks redundant states with `retarget`.
- Computes reachability with `Dfs` and tracks whether `accept_all` is reached.
- Optionally removes contradictory simple conditions with `unclutter`/`clutter`.
- Merges transitions to the same target by OR-combining conditions with `mergetrans`.
- Merges equivalent states through `all_trans_match` and `mergestates`.
- Applies the optional `BUCKY` optimization for special paired-state reductions.
- Prints states and transitions in never-claim syntax through `rev_trans`, `printstate`, and `fsm_print`.

Important interactions:
- Receives transitions from `tl_trans.c` via `addtrans`.
- Uses formula equality/rewrite helpers from `tl_cache.c` and `tl_rewrt.c`.
- Uses `dump_cond` from `tl_trans.c` to print PROMELA conditions.
- `fsm_print` emits to global `tl_out`.

Notable details:
- `accept_all` transitions are printed as atomic assertions designed to flag counterexample acceptance.
- `Max_Red == 0` affects generation of `T0` labels for accepting states.
