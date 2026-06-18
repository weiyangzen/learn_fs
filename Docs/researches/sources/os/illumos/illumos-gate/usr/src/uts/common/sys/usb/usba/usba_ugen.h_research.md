# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugen.h

## Role

Declares the shared USBA-facing interface to the generic USB driver (ugen).

## Key Interfaces

- `usb_ugen_info_t` carries ugen flags and minor-node bit masks for ugen index and instance encoding.
- Defines opaque `usb_ugen_hdl_t`.
- Defines flags `USB_UGEN_ENABLE_PM` and `USB_UGEN_REMOVE_CHILDREN`.
- Declares ugen handle acquisition/release and driver entry wrappers for attach, detach, open, close, power, read, write, poll, disconnect event, and reconnect event.

## Risk Notes

Minor-node mask configuration controls how user-visible ugen device nodes map to endpoints/status nodes. Incorrect masks can alias devices or endpoints.
