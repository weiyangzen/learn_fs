# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vga.c

This file implements VGA/VESA display state, framebuffer rendering, keyboard layout/input capture, and mouse capture.

Key behavior:
- Emulates basic VGA ports for attribute, sequencer, graphics, CRTC, misc output, and palette registers.
- Maintains text mode memory at 0xb8000, framebuffer memory at configured guest physical address, and 256-color palette images.
- Renders text mode using CP437 mapping and Plan 9 draw fonts, including blinking cursor.
- Renders framebuffer modes with dirty-line tracking, colormap expansion for VESA 4/8-bit modes, and direct/scratch image upload paths.
- Parses framebuffer specs such as `text`, raw modes, or `vesa:` mode lists with optional framebuffer address.
- Loads `/dev/kbmap`, maps Plan 9 keyboard runes to PC scan codes, watches `/dev/kbd`, and emits scan-code make/break bytes to the i8042 channel.
- Captures/re-centers mouse input, supports release chord, and forwards relative movement/buttons to PS/2 mouse emulation.
- `vgainit` initializes draw/mouse/keyboard/draw processes and, for VESA, creates a PCI VGA-like device plus framebuffer BAR.

Integration and risks:
- Shares `kbdch`, `mousech`, and `mouseactive` with `io.c`.
- Direct framebuffer writes are polled by `drawproc`; display refresh interval is fixed at roughly 20 ms.
- VESA mode parsing enforces channel compatibility and framebuffer sizing.
