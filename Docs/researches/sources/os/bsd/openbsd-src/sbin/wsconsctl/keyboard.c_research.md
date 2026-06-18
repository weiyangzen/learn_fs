# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/keyboard.c

Implements keyboard-device fields for `wsconsctl`.

Key behavior:
- Defines fields for keyboard type, bell parameters/defaults, keymap, key repeat/defaults, LEDs, encoding, and keyboard backlight.
- `keyboard_get_values()` reads selected fields using `WSKBDIO_*` ioctls.
- `keyboard_put_values()` writes selected fields using corresponding setter ioctls.
- Maintains global `kbmap` backed by `mapdata`, shared with the parser and utility printer.
- Calls `ksymenc()` after reading keyboard encoding so key symbol printing can prefer encoding-specific names.
- Backlight support is optional and marks field dead on `ENOTTY`.

Filesystem/OS relevance:
- Userland bridge to wskbd driver state and keymap mutation.
- Important for studying ioctl-style device configuration and mutable keyboard maps.
