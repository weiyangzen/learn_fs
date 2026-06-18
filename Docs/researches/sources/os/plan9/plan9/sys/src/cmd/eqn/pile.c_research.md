# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/pile.c

Vertical pile/column layout for `eqn`.

Key behavior:
- Builds left-, right-, center-, or default-aligned vertical stacks.
- Computes gap, total height, and baseline based on number of elements and tuned pile parameters.
- Measures maximum width and emits troff vertical/horizontal motion for each element.
- Frees all component registers.

Filesystem relevance:
- Typesetting layout only.
