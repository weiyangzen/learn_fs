# File Research: sources/virtualization/qemu/tools/qemu-vnc/console.c

## Purpose
Implements a minimal standalone `QemuTextConsole` for `qemu-vnc`, backed directly by a raw fd and QEMU’s VT100 emulator.

## Main Structure
`QemuTextConsole` embeds `QemuConsole`, owns a `QemuVT100`, chardev fd, GLib IO watch id, and name.

## Behavior
- Defines QOM type `QEMU_TEXT_CONSOLE`.
- Creates an 80x24 text surface using configured text cell dimensions.
- Initializes VT100 rendering over a pixman display surface.
- Reads from the fd through a GLib IO watch and feeds bytes to `vt100_input()`.
- Flushes VT100 output FIFO back to the fd.
- Updates VNC display regions on VT100 image changes.
- Handles keysyms through `vt100_keysym()`.
- Resizes text console according to VT100 dimensions.

## Filesystem/Storage Relevance
None directly. It supports serial/HMP console exposure through VNC.
