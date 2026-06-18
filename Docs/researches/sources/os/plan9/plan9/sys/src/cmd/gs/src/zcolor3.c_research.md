# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor3.c

Implements the Level 3 `UseCIEColor` setter.

Key behavior:
- `.setuseciecolor` stores the supplied boolean ref into `istate->use_cie_color` and pops it.
- Operator is Level 3-only and intended for controlled initialization/setpagedevice paths, so it does no operand checking.

Dependencies and coupling:
- Complements `.getuseciecolor` in `zcolor.c`.
- Keeps `UseCIEColor` cached in interpreter state for fast checks and language-level-specific behavior.
