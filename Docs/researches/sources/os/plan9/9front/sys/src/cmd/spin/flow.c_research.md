# File Research: sources/os/plan9/9front/sys/src/cmd/spin/flow.c

`flow.c` builds and normalizes Spin’s internal control-flow graph from parsed Promela syntax. It creates `Sequence` and `Element` objects, wires `if`, `do`, `unless`, blocks, labels, breaks, gotos, atomic regions, `d_step` regions, `for`, and `select` constructs.

Sequence construction uses `open_seq()`, `add_seq()`, `add_el()`, and `close_seq()`. `new_el()` assigns per-process and global sequence numbers, while `if_seq()` and `unless_seq()` expand compound constructs into graph nodes with sub-sequences and synthetic target elements. `loose_ends()` later repairs sub-sequence exits so nested blocks flow to the correct next element.

Label handling is central. `set_lab()` records labels with context, block scope, and inline ID. `get_lab()`, `find_lab()`, and `fix_dest()` resolve ordinary and remote label references, including special handling when a label points at a goto. The code rejects labels placed inside ambiguous compound guards and detects jumps into or out of `d_step` with `cross_dsteps()` and `Rjumpslocal()`.

Atomic handling marks ranges with `ATOM`, `L_ATOM`, or `D_ATOM` through `make_atomic()` and `walk_atomic()`, warning or rewriting nested atomic/d_step constructs as needed. `attach_escape()` and `escape_el()` propagate `unless` escape sequences to the states where they can interrupt execution.

The later helpers lower Promela iteration forms. `for_setup()`, `for_index()`, `for_body()`, and `sel_index()` synthesize assignments, loop guards, receives/sends for channel iteration, break destinations, and loop bodies. Validation catches bad index variables, mismatched channel/struct iteration, and reversed constant ranges.

Important risks: much behavior relies on global parser/build state (`cur_s`, `labtab`, `context`, `Fname`, `lineno`, `DstepStart`). Misplaced labels and jumps are fatal because later verifier generation assumes a normalized graph. The file also prunes redundant unlabeled skips, which affects reachability presentation.
