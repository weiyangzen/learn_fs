# File Research: sources/os/plan9/plan9/sys/src/9/boot/usb.c

Boot-time USB support.

Key behavior:
- `usbinit(post)` binds `#u`, starts `/boot/usbd` if `/srv/usb` is absent, waits for first USB disk `/dev/sdU0.0`, and starts partfs if found.
- `mountusb()` mounts `/srv/usb` into `/dev`.
- `startpartfs(post)` starts `/boot/partfs` for first USB disk, optionally posting `/srv/partfs.sdXX`, and passes `sdB0part` environment partitions when available.
- `mountusbparts()` remounts USB and posts partfs.
- `chmod()` adjusts `/srv/partfs.sdXX` mode.

This makes USB keyboard/mouse/storage and USB nvram partitions available during early boot.
