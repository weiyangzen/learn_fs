# File Research: sources/virtualization/qemu/tools/qemu-vnc/qemu-vnc.h

## Purpose
Shared internal header for the standalone `qemu-vnc` tool.

## Contents
- Includes QEMU/GIO/D-Bus/display headers needed across qemu-vnc modules.
- Defines text console geometry constants:
  - `TEXT_COLS 80`
  - `TEXT_ROWS 24`
  - `TEXT_FONT_WIDTH 8`
  - `TEXT_FONT_HEIGHT 16`
- Declares cross-module functions for:
  - text console creation
  - input setup
  - console setup and proxy lookup
  - audio/clipboard/chardev setup
  - peer-to-peer D-Bus thread creation
  - VNC management D-Bus setup, cleanup, leaving signal, and client events

## Filesystem/Storage Relevance
None directly. It is module glue for virtualization UI code.
