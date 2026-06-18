# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.c

Builds Ghostscript configuration/resource tables from `gconf.h`/`gconfig.h`.

Key points:
- Includes generated configuration entries multiple times with different macro definitions.
- Declares configured devices, image types/classes, compositor types, halftones, init procs, and IODevices.
- Builds:
  - compositor list
  - device prototype list
  - device halftone list
  - image class table and count
  - image type table and count
  - initialization procedure table
  - IODevice table and count
- Ensures `%os%` (`gs_iodev_os`) is first in the IODevice table.
- Implements `gs_find_compositor`.
- Implements `gs_lib_device_list`.

Dependencies and interactions:
- Depends on `gconf.h`, which wraps generated `gconfig.h`.
- Exports tables consumed by Ghostscript core initialization and device lookup.

OS/filesystem relevance:
- IODevice registration includes file-related devices such as `%os%`, stdin/stdout/stderr, pipe, null, static, etc., depending on generated config.
