# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_private.h

## Role

Declares unstable/private USBAI-adjacent interfaces used by Solaris/illumos USB client drivers but not part of the stable public USBAI contract.

## Key Interfaces

- Provides current configuration index lookup and string conversion helpers for completion reasons, callback flags, pipe state, device state, return values, plus `usb_rval2errno`.
- Defines `USB_FLAGS_SERIALIZED_CB`, default control pipe timeout, and `usb_pipe_sync_ctrl_xfer()`.
- Defines `usb_event_t` with disconnect, reconnect, pre-suspend, and post-resume callbacks, plus register/unregister and checkpoint-failure APIs.
- Defines logging handle type, log levels, debug-print macros/functions, log-handle allocation/free, and `usb_log`.
- Defines same-device check masks and `usb_check_same_device()`.
- Declares async PM raise/lower helpers and legacy/no-op device power-level helpers.
- Defines opaque serialization handle and functions to initialize/finalize, acquire, try-acquire, and release serialized access, including wait modes and same-thread checking.
- Defines async request scheduling flag `USB_FLAGS_NOQUEUE` and `usb_async_req()`.
- Declares endpoint-index helper and `usba_mk_mctl()`.

## Design Notes

The header labels these interfaces as unstable and marks status classes for migration/removal. It intentionally retains legacy DDK/client compatibility behavior.

## Risk Notes

Although private, these routines are used by real drivers. Changes to callback serialization, PM async behavior, or logging/string helpers can break out-of-tree or legacy clients.
