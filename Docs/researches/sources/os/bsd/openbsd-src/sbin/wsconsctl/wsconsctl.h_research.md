# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.h

Shared header for `wsconsctl`.

Key contents:
- Defines `struct field`, field formats, and field flags.
- Format classes include numeric, boolean, percentage, keyboard/mouse/display types, keyboard encoding/map, mouse scale, display emulation/screen, strings, and mousecfg parameter groups.
- Flags distinguish read-only, write-only, no-auto, modifiable, no-readback, get, set, init, and dead fields.
- Declares shared helper functions and per-device callbacks.
- Includes `dev/wscons/wsksymvar.h` for key symbol/map types.

Filesystem/OS relevance:
- Encodes the field-table abstraction used across keyboard, mouse, and display ioctl modules.
