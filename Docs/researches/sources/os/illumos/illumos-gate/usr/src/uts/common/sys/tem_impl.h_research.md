# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tem_impl.h

## Purpose
Defines private terminal emulator parser, color, screen-buffer, virtual-terminal, rendering-callback, and shared soft-state structures.

## Main Interfaces
- Character/attribute packing:
  - `tem_char_t`
  - `TEM_CHAR()`, `TEM_ATTR()`, `TEM_CHAR_ATTR()`, `TEM_ATTR_ISSET()`
  - attribute flags for reverse, bold, blink, underline, screen reverse, bright colors, transparency, image, and RGB foreground/background
- ANSI/parser constants:
  - `TEM_MAXPARAMS`, `TEM_MAXFKEY`
  - scroll/shift direction constants
  - ANSI color constants
  - parser states `A_STATE_START`, `A_STATE_ESC`, `A_STATE_CSI`, `A_STATE_CSI_QMARK`, `A_STATE_CSI_EQUAL`
- Default terminal dimensions and colors.
- Color and geometry types:
  - `text_color_t`
  - `text_attr_t`
  - `tem_color_t`
  - `tem_pix_pos`, `tem_char_pos`, `tem_size`
  - `term_char_t`
- `struct tem_vt_state`: per-VT parser/output state, locks, framebuffer mode, attributes, ANSI params, tabs, cursor positions, output buffers, pixel scratch area, colors, screen/history buffers, UTF-8 partial state, active/initialized/cursor state, and list node.
- `tem_safe_callbacks_t`: rendering callback table for display, copy, cursor, bit-to-pixel, and clear-screen operations.
- `tem_state_t`: shared terminal emulator soft state, layered device handle, display/pixel dimensions, font, callback set, active terminal, mode-change callback, color map, lock, and VT list.
- Globals:
  - `tems`
  - `tem_safe_text_callbacks`
  - `tem_safe_pix_callbacks`
- Internal functions for layered display/copy/cursor/clear, safe terminal emulation, text/pixel display paths, cursor, clear, color setting, and screen reset/restore.

## Dependencies And Relationships
Includes font, RGB, DDI/LDI, visual I/O, list, public `tem.h`, and annotation headers when not building boot code. Used by console terminal emulation and framebuffer/text console rendering.

## Research Notes
The screen buffer uses a combined 32-bit character/attribute representation with separate foreground/background color arrays in `term_char_t`. Comments note that console history would require revisiting the buffering model.
