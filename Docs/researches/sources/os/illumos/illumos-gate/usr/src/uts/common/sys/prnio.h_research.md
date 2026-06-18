# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/prnio.h

## Purpose
Defines printer-interface ioctl commands, capability/status bits, interface/device-id buffer structures, timeout structure, and 32-bit kernel compatibility structures.

## Main Interfaces
- Ioctls:
  - `PRNIOC_GET_IFCAP`
  - `PRNIOC_SET_IFCAP`
  - `PRNIOC_GET_IFINFO`
  - `PRNIOC_GET_STATUS`
  - `PRNIOC_GET_1284_DEVID`
  - `PRNIOC_GET_1284_STATUS`
  - `PRNIOC_GET_TIMEOUTS`
  - `PRNIOC_SET_TIMEOUTS`
  - `PRNIOC_RESET`
- Capability bits:
  - `PRN_BIDI`
  - `PRN_HOTPLUG`
  - `PRN_1284_DEVID`
  - `PRN_1284_STATUS`
  - `PRN_TIMEOUTS`
  - `PRN_STREAMS`
- Structures:
  - `prn_interface_info`
  - `prn_1284_device_id`
  - `prn_timeouts`
- Recommended interface strings:
  - `PRN_PARALLEL`
  - `PRN_SERIAL`
  - `PRN_USB`
  - `PRN_1394`
- Status bits:
  - `PRN_ONLINE`
  - `PRN_READY`
  - IEEE 1284 status pins: `PRN_1284_NOFAULT`, `PRN_1284_SELECT`, `PRN_1284_PE`, `PRN_1284_BUSY`
- 32-bit kernel structures:
  - `prn_interface_info32`
  - `prn_1284_device_id32`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/ioccom.h`. Intended for printer device drivers and userland printer-management tools.

## Research Notes
Pointer-bearing structures preserve 32-bit layout with explicit filler or alternate `caddr32_t` forms.
