# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/size.c

Point-size control for `eqn`.

Key behavior:
- `setsize()` parses relative and absolute size specifications, tracks absolute-size stack state, and updates current point size.
- `size()` wraps a box in the size transition and restores the prior size.
- `globsize()` changes global equation size and recomputes default script-size delta.

Filesystem relevance:
- Typesetting state only.
