# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/display.c

Implements display-device fields for `wsconsctl`.

Key behavior:
- Defines `display_field_tab` for display type, dimensions, font metrics, emulations, screen types, focus, brightness, contrast, backlight, screen blanking, activity triggers, and font selection.
- `display_get_values()` maps selected fields to `WSDISPLAYIO_*` ioctls, caching shared ioctl results for burner and framebuffer info.
- `display_put_values()` maps writable fields to display ioctls, including focus changes, parameter updates, burner settings, and font selection.
- Unsupported ioctls with `ENOTTY` mark fields `FLG_DEAD`.
- `display_next_device()` enumerates `/dev/ttyC0` through `/dev/ttyJ0`.

Filesystem/OS relevance:
- Userland control surface for wsdisplay kernel drivers.
- Uses ioctl discovery and per-field liveness to support diverse hardware.
