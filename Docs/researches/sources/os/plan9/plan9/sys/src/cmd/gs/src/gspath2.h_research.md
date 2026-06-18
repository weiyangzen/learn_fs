# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspath2.h

Declares Level 2 graphics-state path procedures.

Exports:
- `gs_setbbox`
- Rectangle operators: `gs_rectappend`, `gs_rectclip`, `gs_rectfill`, `gs_rectstroke`

Integration:
- Requires `gsmatrix.h` types and `gs_state`.
- Complements `gspath.h` with rectangle-oriented Level 2 operations implemented elsewhere.

Risk notes:
- Header only; rectangle count and matrix handling contracts are enforced by implementations outside this file.
