# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hubdi.h

## Role

Declares USBA hub-driver nexus interfaces used for root hubs, hub child devices, hub bus operations, reset, and power-budget accounting.

## Key Interfaces

- Declares hub subsystem initialization/destruction hooks.
- Defines `HUBDI_OPS_VERSION_0` and `HUBD_IS_ROOT_HUB`.
- Exposes hub character-device style entry points: open, close, ioctl, and root-hub power.
- Exports `usba_hubdi_busops`.
- Declares DDI autoconfiguration entry points: info, attach, probe, detach, and quiesce.
- Declares root-hub bind/unbind, device reset, and power budget increment/decrement/check helpers.

## Risk Notes

Hub reset and power budget functions sit in the enumeration path. Incorrect accounting can allow over-budget bus power usage or reject valid devices; reset errors can leave child devinfo nodes stale.
