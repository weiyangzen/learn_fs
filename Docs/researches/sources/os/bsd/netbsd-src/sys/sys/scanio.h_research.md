# File Research: sources/os/bsd/netbsd-src/sys/sys/scanio.h

Read completely: 132 lines.

This legacy scanner ioctl header defines `struct scan_io`, scanner control ioctls, image mode constants, and scanner product IDs. Fields include scan dimensions, resolution, origin, image mode, brightness, contrast, quality/speed, computed window size, line/pixel counts, bits per pixel, and scanner type.

Ioctls include `SCIOCGET`, `SCIOCSET`, `SCIOCRESTART`, and `SCIOC_USE_ADF`. `SCAN_BC` compatibility aliases expose older field and ioctl names.

Risks: this is a user/kernel device ABI. Drivers validate scanner-specific ranges and may round to supported settings, so callers are expected to read back state after setting it.
