# File Research: sources/os/plan9/9front/sys/src/9/port/usb.h

Common USB host-controller, endpoint, and device definitions for the Plan 9 kernel USB stack.

Key elements:
- Defines debug-print macros and little-endian 16-bit get/put helpers.
- Declares `Udev`, `Ep`, `Hci`, and `Hciimpl`.
- Defines USB constants for endpoint counts, controller counts, transfer types, speeds, request fields, standard requests, device states, and root-hub port status bits.
- Defines `Hciimpl`, the controller-driver callback table for init, interrupt, endpoint open/stop/close, endpoint read/write, debug formatting, device close, root-port operations, shutdown, and debug control.
- Defines `Hci`, embedding hardware config and the implementation callback table.
- Defines `Ep`, the shared endpoint object with endpoint identity, per-open state, transfer configuration, toggles, polling/iso parameters, timeout, and controller-private aux pointer.
- Defines `Udev`, the shared USB device object with address/state/speed/topology, transaction-translator metadata, endpoint cache, and fake root-hub state.
- Declares `addhcitype()`, `usbmodename`, `Estalled`, and `seprintdata()`.

Dependencies:
- Included by USB controller drivers such as `usbehci.c` and the generic USB device layer.

Notable behavior:
- The header documents ownership expectations: endpoint open prepares hardware state, stop cancels in-flight I/O, close releases hardware state, and stopped endpoints preserve toggles in `Ep`.
