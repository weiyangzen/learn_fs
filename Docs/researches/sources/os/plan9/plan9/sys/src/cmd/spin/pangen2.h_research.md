# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen2.h

This header is mostly embedded source text for generated `pan.c`. It provides the generated verifier’s C preamble, runtime global state, transition-rewriting support, transition-table diagnostics, loop-state discovery, and variable-range logging.

Key contents:
- `Pre0[]`: emitted includes, portability macros, `Offsetof`, and `Printf` prototype.
- `Preamble[]`: generated verifier runtime globals and core structs such as `H_el` and `Trail`.
- Runtime flags and counters for memory, depth, state counts, bitstate, fairness, BFS, multicore, randomized exploration, stack cycling, and trail replay.
- `Tail[]`: generated support functions for `Trans` allocation/copying, partial-order reduction classification, transition rewriting, unless expansion, graph/table output, loop-state tagging, and optional variable range logging.

Important details:
- `Trail` records backtracking state: process id, transition id, atomic/fairness flags, saved queue/process data, old transition pointer, and backup scalar or vector values.
- `H_el` is the stored-state hash table element; its fields vary by `FULLSTACK`, `BITSTATE`, `COLLAPSE`, `BCS`, `AUTO_RESIZE`, `NCORE`, and safety/reachability modes.
- The transition rewriting code (`retrans`) expands choices, pulls transitions through intermediate states, handles `unless`, marks partial-order safety, diagnoses unconditional self-loops and duplicate `else`, and can output text or dot graph transition tables.
- Reduction classification maps generator-side statement types into runtime constants such as `LOCAL`, `Q_FULL_F`, `Q_EMPT_F`, `TIMEOUT_F`, `ALPHA_F`, and `GLOBAL`.
- `crack()` and `dot_crack()` print generated transition tables for debugging and visualization.
- `dfs_table()` and `do_dfs()` identify loop states in process automata.
- `VAR_RANGES` support records assigned byte-range values and prints compact intervals.

Filesystem relevance:
- Indirect. The generated verifier uses standard C headers and can report generated compile options; the surrounding generator writes this text into generated files.
