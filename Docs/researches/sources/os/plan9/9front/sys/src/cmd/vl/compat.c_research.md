# File Research: sources/os/plan9/9front/sys/src/cmd/vl/compat.c

This file only includes `l.h` and the shared C compiler compatibility implementation from `../cc/compat`.

Key behavior:
- Pulls the linker’s compatibility helpers into the `vl` build rather than defining local logic.

Integration and risks:
- Behavior is entirely inherited from `../cc/compat`; changes there affect this linker.
