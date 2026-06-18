# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gconf.c

## Scope

Build-configuration table generator source for Ghostscript resources.

## Key Behavior

- Includes generated `gconf.h` repeatedly with different macro definitions.
- Declares configured compositors, devices, halftones, image classes, image types, init procedures, and IODevices.
- Builds null-terminated tables: compositor list, device list, halftone list, image class table, image type table, init table, and IODevice table.
- Forces `%os%` (`gs_iodev_os`) to be first in the IODevice table.
- Implements `gs_find_compositor` and `gs_lib_device_list`.

## Dependencies

Uses generated `gconf.h` / `gconfig.h` and Ghostscript graphics, device, halftone, image, IODevice, parameter, and compositor headers.

## Risks And Invariants

- The macro names in generated configuration headers are part of the build ABI.
- Table count constants intentionally use `unsigned` to match `gscdefs.h`.
- `%os%` must remain first for default file-device resolution.
