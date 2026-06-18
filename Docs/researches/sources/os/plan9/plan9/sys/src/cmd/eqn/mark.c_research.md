# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/mark.c

Implements equation marks and lineup points.

Key behavior:
- `mark()` records the current horizontal position in troff register 09.
- `lineup()` either marks that a lineup directive exists or emits horizontal motion to align with register 09.
- Sets `markline` state for display output.

Filesystem relevance:
- Typesetting state only.
