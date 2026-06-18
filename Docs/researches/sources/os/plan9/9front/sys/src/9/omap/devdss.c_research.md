# File Research: sources/os/plan9/9front/sys/src/9/omap/devdss.c

Device interface for OMAP Display Subsystem settings.

Key behavior:
- Defines a device with files for display control/settings.
- Uses the `OScreen` state from `screen.h`.
- `settingswrite` parses display configuration text such as geometry/depth/channel/orientation values.
- `screenread` returns current display configuration state.
- `screenwrite` updates settings and validates channel strings through `strtochan`.
- Access is serialized by `dsslck`.

Research notes:
- The device is the control-plane counterpart to `screen.c` display initialization and console drawing.
- It uses Plan 9 device plumbing rather than a generic sysfs-like model.
