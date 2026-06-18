# File Research: sources/os/bsd/freebsd-src/sys/sys/terminal.h

## Scope

This header defines FreeBSD's terminal abstraction layered above TTY and console drivers. It provides packed character/color attributes, terminal class callbacks, terminal state, kernel console registration helpers, and APIs for terminal allocation, TTY creation, resizing, muting, and input.

## APIs And Constants

- Defines `term_char_t` as a 32-bit value containing a Unicode code point, formatting bits, foreground color, and background color.
- Defines extractors `TCHAR_CHARACTER()`, `TCHAR_FORMAT()`, `TCHAR_FGCOLOR()`, and `TCHAR_BGCOLOR()`.
- Defines color/format builders `TCOLOR_FG()`, `TCOLOR_BG()`, `TCOLOR_LIGHT()`, `TCOLOR_DARK()`, and `TFORMAT()`.
- Provides syscons-compatible foreground/background attribute macros, including normal and bright colors plus blink.
- Defines default normal and kernel console attributes through `TERMINAL_NORM_ATTR` and `TERMINAL_KERN_ATTR`.
- Defines callback typedefs for emulator drawing, input boundaries, parameters, cleanup, console probe/getc/grab/ungrab, open notification, ioctl, mmap, and bell handling.
- Defines `struct terminal_class` callback table and `struct terminal` runtime state.
- Under `_KERNEL`, declares `terminal_alloc()`, `terminal_maketty()`, cursor/window/mute/input APIs, `termcn_cnregister()`, `termcn_cnops`, and `TERMINAL_DECLARE_EARLY()`.

## Control Flow And Integration

- Console drivers provide a `terminal_class`; the terminal layer drives output through teken emulator callbacks rather than requiring each driver to implement escape-sequence handling.
- `struct terminal` binds driver softc, mutex, tty, teken emulator, current window size, flags, and console device.
- `TF_CONS` marks console devices that need console locking behavior.
- `TERMINAL_DECLARE_EARLY()` creates a statically initialized console terminal and matching `CONSOLE_DEVICE` for early console registration.
- Input helpers feed Unicode, raw bytes, or special key codes into the terminal/TTY layer.

## Dependencies

- Includes kernel parameters, lock/mutex definitions, console declarations, linker set support, tty ioctl structures, teken terminal emulator types, and syscons/teken option headers.
- Integrates with the TTY subsystem, kernel console framework, DDB/panic console paths, and framebuffer/text console drivers.

## Risks And Invariants

- `term_char_t` bit allocation is part of the terminal driver contract; changing it affects every renderer using stored cell values.
- Teken uses UTF-8/Unicode semantics; drivers should not reinterpret character bits as legacy bytes.
- Console paths can run in panic/debugger contexts, so callbacks and locks must respect those constraints.
- The early terminal declaration relies on static initialization only; fields not initialized there must tolerate zero defaults.
