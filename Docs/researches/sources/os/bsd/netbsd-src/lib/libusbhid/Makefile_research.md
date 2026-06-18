# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/Makefile

Build definition for NetBSD `libusbhid`.

Key points:
- Builds library `usbhid` from:
  - `descr.c`
  - `parse.c`
  - `usage.c`
  - `data.c`
- Installs public header `usbhid.h`.
- Installs manual page `usbhid.3` and many MLINK aliases.
- Installs `usb_hid_usages` into `/usr/share/misc` when `MKSHARE != no`.

Role in subsystem:
- Builds the HID report descriptor parsing and report data helper library.
