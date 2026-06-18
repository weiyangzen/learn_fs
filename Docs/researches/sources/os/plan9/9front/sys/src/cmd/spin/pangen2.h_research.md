# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen2.h

Template header consumed by `pangen2.c`. It defines large `static const char *` arrays that are copied into generated verifier files.

Key template groups:
- `Pre0`: generated C includes, portability typedef/macros, and basic prototypes.
- `Separate`: generated global storage for transition tables, process/channel offsets, state-vector size, trail prefix, block-on-queue status, and PEG counters.
- `Preamble`: generated verifier globals, stack/hash state, memory counters, hash constants, search flags, randomization flags, BFS/bitstate hooks, and runtime function pointers.
- `Tail`: generated transition helpers and table rewriting logic.

Key generated behavior:
- Defines `settr` and `cpytr` for creating/copying `Trans` records.
- Implements reduction classification helpers `srinc_set`, `srunc`, and `mark_safety`.
- Implements `retrans`, which rewrites transition tables by flattening choice-in-choice transitions, pulling single-step gotos, adding unless escapes, marking reduction safety, detecting mixed selections, propagating stop states, optionally dumping table/DOT output, computing loop states, and reversing transition order when requested.
- Implements `imed`, `tagtable`, `dfs_table`, and `do_dfs` for intermediate-state metadata, reachability traversal, transition-id lookup, and loop-state tagging.
- Implements `crack` and `dot_crack` for human-readable and Graphviz transition-table diagnostics.
- Under `VAR_RANGES`, records and dumps assigned byte-range values for variables.

Dependencies:
- Expects generated symbols and arrays such as `trans`, `procname`, `Btypes`, `accpstate`, `progstate`, `stopstate`, `visstate`, `mapstate`, `t_id_lkup`, `PanSource`, `NTRANS`, `DELTA`, and `HAS_UNLESS`.
- Runtime behavior is tied to macros emitted by `pangen2.c` and structure declarations emitted by `pangen3.h`.

Research notes:
- Despite its `.h` name, this is generated-code payload, not normal API declarations.
- The large hash-constant table and many compile-option branches make this a compatibility-sensitive verifier runtime template.
