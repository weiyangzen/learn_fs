# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/dblook.c

Small diagnostic program for the `faces` database lookup logic.

Key behavior:
- Expects `name domain`.
- Calls `findfile(&f, domain, name)` and prints the resolved face image path.
- Provides a stub `killall()` because shared face database code may call it on fatal conditions.

Dependencies:
- Reuses `faces.h` and `facedb.c` behavior.

Risks and invariants:
- Does not initialize graphics display state; it only exercises path lookup, not image loading.
