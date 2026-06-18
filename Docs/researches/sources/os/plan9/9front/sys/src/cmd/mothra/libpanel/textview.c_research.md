# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textview.c

Implements a scrollable rich-text viewer panel.

Key behavior:
- Formats rich text with `pl_rtfmt()` when the visible width changes.
- Draws rich text with current x/y offsets and updates attached scrollbars.
- Mouse handling selects hot rich-text ranges, passes events into embedded panel runs, and invokes hit callbacks for single hot items.
- Supports vertical and horizontal scrolling through `pl_rtredraw()`.
- Exposes get/set vertical position and snarfing selected rich text.

Important dependencies: `rtext.c`, scrollbars, panel hit priority.

Notable risks:
- Embedded panels inside rich text can capture mouse state through `REMOUSE`.
- Reformatting is tied to width changes, so text metrics and panel sizes must be stable.
