# File Research: sources/os/plan9/plan9/sys/src/9/bcm/etherusb.c

Kernel proxy driver for USB Ethernet devices.

Key behavior:
- Registers an Ethernet card type `"usb"` through `etherusblink()`.
- Does not enumerate USB devices itself; instead `bind` control messages provide USB input/output endpoint paths, MAC address, buffer size, and max packet size.
- Supports CDC, ASIX, and SMSC framing with per-device unpack/transmit functions.
- Receive path runs `etherusbproc`, repeatedly reading USB endpoint blocks and unpacking one or more Ethernet frames into `etheriq()`.
- Transmit path drains Ethernet output queue and wraps frames according to the selected USB Ethernet type before writing endpoint data.
- Exposes interface stats for rx/tx buffers and packets.
- `unbind()` closes channels and frees buffers.

This bridges the generic Ethernet stack to USB endpoint files created by `devusb.c`/`usbd`.
