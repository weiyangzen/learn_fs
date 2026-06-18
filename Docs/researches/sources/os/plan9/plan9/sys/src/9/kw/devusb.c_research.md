# File Research: sources/os/plan9/plan9/sys/src/9/kw/devusb.c

## Purpose
Implements the Plan 9 USB device framework `#u`. It manages host controller registration/probing, root-hub representation, device and endpoint allocation, endpoint filesystem layout, endpoint control commands, and endpoint I/O dispatch to HCI-specific callbacks.

## Filesystem Model
- Root `#u` lists `usb` and any named endpoint aliases.
- `#u/usb` lists global `ctl` and endpoint directories named `epN.M`.
- Each endpoint directory contains:
  - `data`: exclusive endpoint I/O file.
  - `ctl`: endpoint status/control file.
- Endpoint 0 (`epN.0`) represents a device control endpoint and owns per-device state.

## Main Data Structures and Globals
- `Hcitype`: host-controller type string plus reset callback.
- `hcitypes`, `hcis`: registered/probed host-controller drivers.
- `eps`: global endpoint table, protected by `epslck`.
- `epmax`, `usbidgen`: endpoint and USB device address allocation state.
- `Ep` and `Udev` are defined in `../port/usb.h` and used throughout.

## Endpoint and Device Allocation
- `addhcitype` registers a controller type.
- `epalloc`, `getep`, and `putep` allocate, refcount, publish, and free endpoint structures.
- `newdev` creates endpoint 0 and a `Udev`, assigning speed, state, root-hub status, and default control endpoint settings.
- `newdevep` creates nonzero endpoints on an existing device and fills defaults for control, interrupt, and isochronous endpoints.
- `newusbid` monotonically allocates USB addresses and warns past the 7-bit address range.

## Host Controller Flow
- `usbreset` probes HCI types and controller slots using registered reset callbacks.
- `hciprobe` allocates an `Hci`, calls its reset callback, enables interrupts, and reports the root endpoint path.
- `usbinit` calls HCI init callbacks and creates a root-hub device for each controller.
- `usbshutdown` calls HCI shutdown callbacks.

## I/O Flow
- `usbopen` validates endpoint availability, mode, configuration, exclusive use, computes load, and calls `ep->hp->epopen`.
- `usbread` dispatches directory/control reads, root-hub emulated reads, or HCI `epread`.
- `usbwrite` dispatches global/endpoint control writes, root-hub emulated setup writes, or HCI `epwrite`.
- `usbclose` closes active endpoint I/O through HCI `epclose` and releases endpoint refs.

## Control Interface
Global `#u/usb/ctl`:
- `debug on|off|n`: toggles framework and HCI debug.
- `dump`: prints endpoint and HCI state.

Endpoint `ctl` commands include:
- `new nb ctl|bulk|intr|iso r|w|rw`: create endpoint.
- `newdev full|low|high port`: create a child device from a hub endpoint.
- `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `address`, `detach`, `debug`, `clrhalt`, `name`, `timeout`, `reset`.

## Root Hub Emulation
- `rhubwrite` accepts limited class/port setup requests for port enable, port reset, and get status.
- `rhubread` returns the pending root-hub reply.

## Dependencies and Integration
Relies on HCI drivers for actual controller operations, Plan 9 device helpers, endpoint and USB constants from `usb.h`, interrupt setup from HCI reset, and user-space `usbd` for enumeration/configuration policy.

## Risks and Notes
The interface intentionally exposes a nonstandard USB control model to user space. Endpoint lifetime is reference-counted but intertwined with filesystem refs, open refs, and device detach handling, making `putep` paths sensitive. Bandwidth/load accounting is rough and based on worst-case microsecond estimates.
