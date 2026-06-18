# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.h

Header for `mousecfg.c`.

Key contents:
- Extern declarations for global `struct wsmouse_parameters` field groups.
- Extern `cfg_touchpad` flag.
- Prototypes for initialization, get/put, print, and parse helpers.

Filesystem/OS relevance:
- Exposes mouse parameter groups to `mouse.c` and generic field formatting code.
