# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/flow.c

SPIN control-flow graph construction.

Key behavior:
- Opens/closes statement sequences and assigns local/global sequence numbers.
- Builds `Element` nodes for ordinary statements, `if`, `do`, `unless`, atomic, non-atomic, and `d_step` sequences.
- Rewrites labels and tracks label scopes, inline ids, and remote label references.
- Validates that jumps do not enter or leave `d_step` improperly.
- Attaches `unless` escape sequences to normal execution paths.
- Constructs `for` and `select` loop forms by lowering them to assignments, guards, receives/sends, and `do` loops.
- Marks atomic/d_step sequences and warns about nested or invalid constructs.

Important details:
- `loose_ends()` patches nested sequence exits after parsing.
- `if_seq()` moves `else` branches to the end and warns on dubious `else` with channel I/O.
- Labels on gotos may be moved to inserted skip nodes to preserve jump targets.
- `dumplabels()` reports label-to-sequence mappings.

Filesystem relevance:
- None directly; internal graph builder for the SPIN tool.
