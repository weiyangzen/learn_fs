# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/event.h

This small header defines event constants and a compact event payload structure.

Definitions:
- `BSIZE` is 4000.
- Event indices: `MOUSE`, `KBD`, `HOST`.
- Block flags: `HOST_BLOCKED`, `KBD_BLOCKED`.
- `IOEvent` contains a short key, short size, and `data[BSIZE]`.

Role:
- It appears to describe an older or alternate event representation. The main VT files use Plan 9 `<event.h>` directly rather than this `IOEvent` in the read code shown.
