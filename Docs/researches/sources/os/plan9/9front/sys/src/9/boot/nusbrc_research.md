# File Research: sources/os/plan9/9front/sys/src/9/boot/nusbrc

Boot-time USB enumeration and auto-attach script.

Key responsibilities:
- Binds USB device namespace into `/dev`.
- Creates private USB state directories under shared memory.
- Starts `nusb/usbd`.
- Reads USB attach/detach events and starts appropriate helpers for Ethernet, keyboards, disks, and selected special devices.
- Detects common USB Ethernet chipsets and passes type-specific arguments.
- For USB disks, runs `diskparts`, detects DOS partitions, and starts `dossrv`.
- Cleans shared-memory state on detach.
- Waits for enumeration completion via `/env/usbbusy`, then binds USB device/net namespaces into `/dev` and `/net`.

Important behavior:
- Avoids attaching selected HID-like devices as keyboards.
- Special-cases Raspberry Pi USB Ethernet so it appears as `/net/etherU0`.

Dependencies:
- `nusb/usbd`, `nusb/ether`, `nusb/disk`, `nusb/kb`, `diskparts`, `fstype`, `dossrv`, shared-memory device `#σ`, and rc event handling.
