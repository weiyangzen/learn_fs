# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/usbd.c

USB daemon hub enumeration and control service.

Major responsibilities:
- Creates root/non-root `Hub` objects, configures hub descriptors, powers ports, and maintains global hub list.
- Polls all hub ports periodically; detects attach, detach, suspend/resume, reset requests, and status changes.
- `portattach` performs USB enumeration: enable/reset port, create kernel USB device, set address, get max packet, load descriptors, set configuration, and store `Dev`.
- `startdev` is called after successful port attach to launch the appropriate driver.
- `portdetach` tears down child hubs/devices, releases driver numbering, detaches kernel endpoints, unregisters USB file systems, and closes devices.
- `portresetwanted`/`portreset` implement reset requests signaled through endpoint control files.
- `work` serializes enumeration across hubs to avoid default-address conflicts.
- Exposes `usbdctl` as a small `Usbfs` file with commands for dump, exit, debug level, fsdebug, driver args, auto/noauto.
- Reads environment variables for debug and driver args.
- `threadmain` binds `#u`, starts root hub discovery, starts `usbdirfs`, registers `usbdctl`, and mounts/posts the USB service.

Design notes:
- Root hubs are configured by reading kernel control data rather than a standard descriptor.
- Non-root hub interrupt endpoints are not used; polling is intentional.
- Comments describe reset/event limitations and the lack of a kernel event file.
