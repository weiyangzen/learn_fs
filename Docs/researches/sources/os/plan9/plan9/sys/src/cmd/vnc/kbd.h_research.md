# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbd.h

Shared keyboard/snarf declarations for the VNC console and keyboard paths.

Key contents:
- Defines `Snarf` as a locked buffer with version, length, and data pointer.
- Sets `MAXSNARF` to 100 KiB.
- Declares global `snarf`.
- Declares Latin compose, keyboard input, screen output, VNC keyboard input, and snarf update functions.

Role:
- Connects `devcons.c`, `kbds.c`, `latin1.c`, and screen output code.

Risks:
- Snarf ownership is transferred by pointer, so callers must follow the close/commit convention.
