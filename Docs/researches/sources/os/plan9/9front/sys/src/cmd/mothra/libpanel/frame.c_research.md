# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/frame.c

Implements a framed container panel.

Key behavior:
- Draws a filled frame box.
- Sizes itself as its child size plus frame interior.
- Provides child-space inset based on frame geometry.
- Does not handle mouse or keyboard events itself.

Important dependencies: `pl_box`, `pl_boxsize`, `pl_interior`.

Notable risks:
- Child layout depends on `pl_childspaceframe()` matching draw geometry.
