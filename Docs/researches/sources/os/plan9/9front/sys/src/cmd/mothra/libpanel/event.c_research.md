# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/event.c

Routes keyboard and mouse events through a panel tree.

Key behavior:
- `plgrabkb()` changes keyboard focus and redraws the old focus owner.
- `plkeyboard()` sends Runes to the focused panel.
- `pl_ptinpanel()` finds the most leafward, highest-priority panel containing a point.
- `plmouse()` sends mouse events, synthesizes `OUT` when leaving a previous panel, and supports `REMOUSE` capture.

Important dependencies: panel priority functions and widget `hit` handlers.

Notable risks:
- Hit dispatch depends on panel rectangles being current from `plpack`.
- `REMOUSE` capture is controlled by widget hit return values.
