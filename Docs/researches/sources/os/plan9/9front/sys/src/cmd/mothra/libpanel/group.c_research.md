# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/group.c

Implements a grouped container panel.

Key behavior:
- Draws a frame outline rather than a filled frame.
- Sizes and insets children like a frame.
- Does not directly process input.

Important dependencies: `pl_outline`, `pl_boxsize`, `pl_interior`.

Notable risks:
- Visual difference from `frame` is only draw behavior; layout behavior remains frame-like.
