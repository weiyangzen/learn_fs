# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/cga.tiny.c

## Purpose
Tiny CGA text console implementation for the decompressor/early boot environment.

## Main Interfaces
- Exports `cgainit()`.
- Exports `cgaputc(int c)`.

## Implementation Notes
- Writes directly to CGA text memory at physical `0xB8000`.
- Reads and writes CRTC cursor registers through ports `0x3D4/0x3D5`.
- Handles newline, tab, backspace, ordinary characters, cursor movement, and scrolling.
- Uses fixed 80x25 geometry and grey-on-black attribute.

## Dependencies And Risks
- Assumes text-mode CGA-compatible framebuffer at `0xB8000`.
- No locking or bounds beyond simple scroll behavior.
