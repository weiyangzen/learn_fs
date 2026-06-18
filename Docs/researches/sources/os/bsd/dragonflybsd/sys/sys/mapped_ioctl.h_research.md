# File Research: sources/os/bsd/dragonflybsd/sys/sys/mapped_ioctl.h

Defines an ioctl translation/mapping framework. It declares wrapper and command mapping callback types, `ioctl_map_range`, range construction macros, `ioctl_map`, and `ioctl_map_handler`.

Kernel APIs register/unregister handlers and route `mapped_ioctl()` calls. Useful for compatibility layers where ioctl command numbers or payload layouts must be translated before dispatching to underlying file/device handlers.
