# File Research: sources/os/bsd/freebsd-src/sys/sys/backlight.h

## Purpose
`backlight.h` defines the user/kernel ioctl ABI for FreeBSD backlight devices.

## Main Interfaces
- `BACKLIGHTMAXLEVELS` is 100, and `struct backlight_props` carries current brightness, number of levels, and the level table.
- `enum backlight_info_type` distinguishes panel and keyboard backlights.
- `struct backlight_info` carries a fixed-size device name and type.
- Ioctls: `BACKLIGHTGETSTATUS`, `BACKLIGHTUPDATESTATUS`, and `BACKLIGHTGETINFO`.

## Implementation Notes
The interface uses fixed-size arrays for ABI simplicity. Brightness and levels are `uint32_t`, which makes this a generic control plane rather than a direct hardware register format.

## Dependencies and Constraints
Includes `sys/types.h`. Callers must not assume more than 100 levels or names longer than `BACKLIGHTMAXNAMELENGTH`.
