# File Research: sources/os/plan9/9front/sys/src/9/boot/devusb.proto

Prototype extension adding USB boot support tools.

Key contents:
- Includes `nusb/usbd`, `nusb/ether`, `nusb/disk`, and `nusb/kb`.
- Installs `nusbrc` into `rc/bin`.

Role:
- Adds USB enumeration, USB Ethernet, USB storage, and USB keyboard support to a boot image.
