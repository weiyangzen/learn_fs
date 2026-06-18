# File Research: sources/os/plan9/9front/sys/src/9/sgi/devkbd.c

Implements the SGI keyboard/mouse controller device as Plan 9 device `#b`. It exposes `scancode` for raw keyboard scancodes and `leds` for lock LED control.

The controller is i8042-like but accessed through SGI HPC3 keyboard/mouse MMIO. `kbdinit` maps the controller, initializes a nonblocking queue, drains pending bytes, reads/modifies the controller command byte, enables keyboard interrupts/scancode set 1, and adds a clock poll hook. `i8042intr` routes aux-port bytes to `sgimouseputc` and keyboard bytes to the scancode queue.

Open of `scancode` is eve-only and exclusive via a ref count. LED writes parse a small integer and send the 0xed keyboard LED command.
