# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devusb.c

Generic Plan 9 USB device filesystem framework for `#u`.

Key behavior:
- Exposes `/usb/ctl` plus per-endpoint directories `epN.M` with `data` and `ctl`.
- Maintains registered HCI types, active HCIs, endpoint table, endpoint refs, and USB device IDs.
- Userland enumeration is expected: `usbd` creates devices/endpoints and configures them through endpoint control files.
- Supports endpoint controls such as `new`, `newdev`, `hub`, `speed`, `maxpkt`, `ntds`, `pollival`, `samplesz`, `hz`, `info`, `detach`, `address`, `debug`, `clrhalt`, `name`, `timeout`, and `reset`.
- Data opens are exclusive and dispatch reads/writes to HCI callbacks (`epread`, `epwrite`, `epopen`, `epclose`).
- Root hub behavior is emulated for port enable/reset/status control requests.
- `usbreset()` probes registered HCI types; `usbinit()` creates root hub device endpoints.
- `usbshutdown()` calls controller shutdown hooks.

Important design note: this is deliberately a filesystem-facing USB endpoint broker, not a full in-kernel USB enumerator. The controller-specific implementation is in `usbdwc.c`.
