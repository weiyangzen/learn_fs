# File Research: sources/os/plan9/plan9/sys/src/9/omap/devusb.c

Implements the generic USB `#u` device filesystem and endpoint framework for host-controller drivers.

Key points:
- Provides root `#u`, `#u/usb/ctl`, and per-endpoint directories `epN.M` with `data` and `ctl` files.
- Expects user-level `usbd` to enumerate devices, allocate endpoints, configure devices, and start drivers.
- Registers HCI backend types through `addhcitype()` and probes them in `usbreset()`.
- `usbinit()` initializes each HCI and creates a permanent root-hub control endpoint for each controller.
- Maintains global endpoint table `eps[]`, endpoint refs, maximum used endpoint index, and USB device address generator.
- `newdev()` creates endpoint 0 and a `Udev`; `newdevep()` adds nonzero endpoints under a device.
- `usbgen()` dynamically lists the USB filesystem, including named endpoints exposed directly under `#u`.
- `usbopen()` enforces exclusive data endpoint use, direction permissions, endpoint type configuration, HCI `epopen()`, and transfer-load calculation.
- `usbread()`/`usbwrite()` delegate data transfers to HCI callbacks, with fake root-hub control handling for port enable/reset/status.
- `ctlread()` reports all endpoints or one endpoint; after `newdev`, it returns the new endpoint name via `c->aux`.
- `epctl()` implements endpoint commands: `new`, `newdev`, `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `detach`, `address`, `debug`, `clrhalt`, `name`, `timeout`, and `reset`.
- `usbctl()` handles global debug and dump commands.
- `usbshutdown()` calls each HCI shutdown hook.

Dependencies and interactions:
- HCI drivers implement `Hci` callbacks for reset/init/interrupt/endpoint I/O/port operations.
- USB clocks and resets are configured by `archomap.c`.
- Uses Plan 9 device, queue, and ref-counting patterns from the port kernel.

Research relevance:
- Central USB endpoint abstraction and filesystem API used by OMAP USB host-controller support.
