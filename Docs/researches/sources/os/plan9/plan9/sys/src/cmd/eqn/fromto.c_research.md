# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/fromto.c

Implements `from`/`to` limits.

Key behavior:
- Builds a new box containing a base expression plus optional lower and upper limit boxes.
- Measures widths, centers components, adjusts point size for limits, and computes combined height/baseline.
- Frees consumed component registers.

Filesystem relevance:
- Typesetting layout only.
