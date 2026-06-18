# File Research: sources/os/plan9/plan9/sys/src/9/pc/devusb.c

Read completely: 1474 lines.

This file implements the generic Plan 9 USB device framework, exposed as `#u`.

Key behavior:
- Maintains host-controller instances, USB devices, and endpoints.
- Creates root hub endpoint zero for every detected HCI.
- Exposes `#u/usb/ctl` plus dynamic endpoint directories `epN.M`.
- Each endpoint directory contains `data` and `ctl`.
- Allows endpoint aliases at top-level `#u` through the `name` endpoint control.
- User-space enumeration is expected; this kernel driver provides endpoint creation, configuration, and I/O routing.
- Controller-specific behavior is delegated through `Hci` methods from UHCI/OHCI/EHCI drivers.

Important interfaces:
- Device name: `usb`, rune `L'u'`.
- Global control commands: `debug`, `dump`.
- Endpoint control commands include:
  - `new`
  - `newdev`
  - `hub`
  - `speed`
  - `maxpkt`
  - `ntds`
  - `pollival`
  - `samplesz`
  - `hz`
  - `info`
  - `detach`
  - `address`
  - `debug`
  - `clrhalt`
  - `name`
  - `timeout`
  - `reset`

Key internal pieces:
- `addhcitype()` registers HCI driver reset functions.
- `usbreset()` probes configured and auto-detected HCIs.
- `usbinit()` creates root hubs.
- `epalloc()`, `getep()`, and `putep()` manage endpoint lifetime.
- `newdev()` creates endpoint zero and device state.
- `newdevep()` creates non-zero endpoints for a device.
- `rhubread()` and `rhubwrite()` emulate minimal root-hub class requests.
- `usbload()` estimates periodic endpoint bandwidth cost.

Research notes:
- Data files are exclusive-use and enforce endpoint direction.
- Endpoint configuration generally must happen before opening the data file.
- Detached devices transition to `Ddetach` and release endpoint filesystem references.
