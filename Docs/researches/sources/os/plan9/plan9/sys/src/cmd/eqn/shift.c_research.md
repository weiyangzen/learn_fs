# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/shift.c

Subscript and superscript layout for `eqn`.

Key behavior:
- Dispatches to single sub/sup or combined sub-and-sup layout.
- Computes script vertical shifts, point-size changes, spacing adjustments, height, and baseline.
- Handles special italic spacing cases and right-class propagation.
- Frees consumed script registers and temporary registers.

Filesystem relevance:
- Typesetting layout only.
