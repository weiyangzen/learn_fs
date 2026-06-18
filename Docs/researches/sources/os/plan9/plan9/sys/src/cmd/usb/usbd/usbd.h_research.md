# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.h

Shared header for `usbd`.

Defines:
- Hub descriptor constants, hub/port feature selectors, port status bits, port states, enumeration delays, polling interval, and driver table CSP match flags.
- `Hub`, containing descriptor-derived hub state, ports, root flag, USB device, and global list link.
- `Port`, containing state, previous status, removable/power flags, attached `Dev`, child hub, assigned device number, and number-mask pointer.
- `DHub`, the USB hub descriptor layout.
- `Devtab`, the driver dispatch table entry with name, optional embedded init function, CSPs, VID/DID, args, device-number mask, and noauto flag.
- Exports `newhub`, `startdev`, device-number helpers, `threadmain`, and `usbdfsops`.

This header ties `usbd.c`, `dev.c`, and generated device tables together.
