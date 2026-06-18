# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/fns.h

Cross-file function declarations and small macros for Abaco.

Key contents:
- Rune allocation/move helpers.
- HTML layout/table declarations.
- Timer declarations.
- Text command operations.
- Scroll, font, charset, URL, drawing, image, execution, refresh, mouse, and window-helper declarations.
- Selection hit-testing and layout hit-testing helpers.

Dependencies:
- Complements `dat.h`; both are included by most Abaco C files.
- Uses Plan 9 and libhtml types.

Notable risks:
- Functions are grouped by subsystem but not namespace-scoped; symbol collisions are possible in the old C style.
