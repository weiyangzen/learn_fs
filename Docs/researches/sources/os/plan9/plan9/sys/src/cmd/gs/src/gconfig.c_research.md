# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfig.c

Duplicate configuration table builder matching `gconf.c`.

Key points:
- Contents are effectively the same as `gconf.c`.
- Repeatedly includes `gconf.h` under different macro definitions to declare and populate Ghostscript resource tables.
- Exports configured compositor, device, halftone, image class/type, initialization, and IODevice tables.
- Implements `gs_find_compositor` and `gs_lib_device_list`.

Dependencies and interactions:
- Uses generated `gconfig.h` through `gconf.h`.
- Provides global configuration data for Ghostscript startup and device lookup.

OS/filesystem relevance:
- Includes the IODevice table, with `%os%` first as the default file device.
