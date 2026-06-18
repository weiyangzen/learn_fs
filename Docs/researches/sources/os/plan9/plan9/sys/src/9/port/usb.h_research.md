# File Research: sources/os/plan9/plan9/sys/src/9/port/usb.h

## Role

Defines common USB device, endpoint, and host-controller abstractions for Plan 9 USB controller drivers.

## Main Definitions

Constants cover endpoint/device limits, transfer types, speeds, standard request fields, request codes, device states, and hub-style port status bits. `GET2` and `PUT2` encode little-endian USB 16-bit fields.

## Main Structures

`Hciimpl` is the controller driver vtable: initialization, interrupt handling, endpoint open/close/read/write, root-port control, shutdown, and debug hooks.

`Hci` embeds hardware configuration plus the implementation hooks. `Ep` models a kernel USB endpoint, including stable identity fields, QLock-protected configuration, transfer type, timing, saved toggles, and controller-private `aux`. `Udev` models per-device state and cached endpoints.

## Interfaces

Exports `addhcitype`, `usbmodename`, and `seprintdata`.

## Risks

The header centralizes contracts but does not enforce concurrency. Controller drivers must honor endpoint locking, saved toggle behavior, root-hub status bit format, and half/full/high-speed transfer semantics.
