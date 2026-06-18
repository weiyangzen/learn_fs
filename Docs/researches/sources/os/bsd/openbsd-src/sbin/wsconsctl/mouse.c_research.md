# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mouse.c

Implements mouse and touchpad fields for `wsconsctl`.

Key behavior:
- Defines fields for resolution, samplerate, type, rawmode, calibration scale, reverse scrolling, touchpad tapping, multitouch buttons, scaling, swapsides, disable, edges, and raw parameter access.
- `mouse_init()` calls `mousecfg_init()` and hides unsupported configuration fields depending on device type and feature availability.
- `mouse_get_values()` reads mouse type and calibration data, then reads mousecfg-backed fields.
- `mouse_put_values()` writes resolution, calibration/raw mode, and mousecfg parameters.
- `mouse_next_device()` enumerates `/dev/wsmouseN`.

Filesystem/OS relevance:
- Shows combined legacy wsmouse calibration ioctls and newer parameter-array based configuration.
