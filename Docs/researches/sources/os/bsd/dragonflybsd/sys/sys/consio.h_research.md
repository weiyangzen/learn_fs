# File Research: sources/os/bsd/dragonflybsd/sys/sys/consio.h

Console, virtual terminal, video mode, font, mouse, screen saver, and terminal-emulator ioctl ABI.

Key responsibilities:
- Defines historical KD/GIO/PIO/CONS ioctl constants for text/graphics/pixel modes, border color, raster setup, screen maps, colors, adapter/mode info, blanking, cursor, bell, history, font data, screenshots, terminal info, keyboard selection, and vty switching.
- Defines mouse ioctl structures for position, mode, events, and operations.
- Defines font payload types for 8x8, 8x14, and 8x16 font tables.
- Defines `vid_info`, `scrshot`, `term_info`, and `vt_mode`.
- Declares kernel globals controlling break-to-debugger behavior.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Some ioctl payload typedefs reference framebuffer/video types declared in other headers.

Notable risks:
- Many ioctl numbers and names are historical compatibility ABI and cannot be freely renumbered.
- Multiple ioctls carry user pointers, including screenshot buffers.
