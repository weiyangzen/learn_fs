# File Research: sources/os/bsd/dragonflybsd/sys/sys/backlight.h

Read completely: 64 lines.

This header defines the backlight ioctl interface.

Key contents:
- Maximum brightness level count of 100.
- `struct backlight_props` with current brightness, number of levels, and level table.
- Backlight info type enum for panel and keyboard backlights.
- `struct backlight_info` with fixed-size name and type.
- Ioctls for get status, update status, and get info.

Security/reliability notes:
- No runtime logic. The ioctl structures are ABI-sensitive.
- Kernel ioctl handlers must validate `nlevels` against `BACKLIGHTMAXLEVELS`.
