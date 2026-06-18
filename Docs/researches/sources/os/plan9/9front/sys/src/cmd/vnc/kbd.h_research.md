# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbd.h

## Role

`kbd.h` declares shared keyboard and clipboard state for the VNC server and viewer support files.

## Contents

- Defines `Snarf`, a qlock-protected clipboard buffer with version, byte count, and buffer pointer.
- Defines `MAXSNARF` as 100 KiB.
- Declares global `snarf` and `kbdin`.
- Declares `screenputs()`, `vncputc()`, and `setsnarf()`.

## Notable Limitations And Risk Areas

- `Snarf` ownership is manual: callers must know when `setsnarf()` takes ownership of a buffer.
- `kbdin` is a process-global file descriptor used by VNC key injection.
