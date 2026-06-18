# File Research: sources/os/plan9/plan9/sys/src/9/kw/cga.c

## Purpose
Implements a simple CGA-style text console backend using memory at `0xB8000`.

## Behavior
- Maintains `cgapos` as a byte offset into the 80x25 text buffer.
- `cgascreenputc` handles newline, tab, backspace, normal character output, scrolling, and cursor update.
- `cgascreenputs` serializes writes with `cgascreenlock`, avoiding deadlock if called from interrupt context.
- `screeninit` reads the cursor position from CGA registers and installs `cgascreenputs` as `screenputs`.

## Dependencies and Integration
Uses Plan 9 screen output hook `screenputs`, kernel lock primitives, and `KADDR` mapping.

## Risks and Notes
`inb` and `outb` are TODO stubs in this port, so cursor register access is nonfunctional unless replaced elsewhere. This file appears more like inherited PC console code than real Kirkwood display hardware support.
