# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/canvas.c

Implements a generic leaf panel that delegates drawing and mouse handling to caller callbacks.

Key behavior:
- Stores optional draw and hit callbacks.
- Size request is zero; layout sizing comes from parent flags or external constraints.
- Ignores keyboard input.

Important dependencies: libpanel core `pl_newpanel`.

Notable risks:
- Caller-owned callbacks must know the panel rectangle and draw target.
