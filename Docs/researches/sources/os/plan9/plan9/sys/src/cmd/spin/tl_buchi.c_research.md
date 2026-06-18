# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_buchi.c

Converts translated automaton graph transitions into a Promela `never` claim.

Key responsibilities:
- Maintains `State` and `Transition` lists representing the output Buchi automaton.
- Adds transitions from graph generation via `addtrans`.
- Prunes conditions, removes impossible/simple contradictory transitions, merges equivalent transitions and states, and emits final Promela code with `fsm_print`.
- Handles acceptance-state naming, reachability, `accept_all`, and optional optimizations.

Important functions:
- `Prune`: removes non-printable/non-state-condition portions from formulas.
- `unclutter`/`clutter`: detect simple contradictory conjunctions like `p && !p`.
- `mergetrans`: combines transitions to the same target by OR-ing conditions.
- `mergestates`: removes states with equivalent transition sets and matching acceptance.
- `buckyballs`: optional optimization for mutually equivalent accepting cycles.
- `rev_trans`/`printstate`: output Promela guarded commands.

Data flow:
- `tl_trans.c` calls `addtrans`, then `fsm_print`.
- Transition conditions are duplicated, pruned, rewritten, and printed through `dump_cond`.

Risks/quirks:
- Several optimizations are suppressed when `tl_verbose` is enabled.
- State retargeting uses string-name matching.
- Fixed-size buffers assume generated names fit expected lengths.
