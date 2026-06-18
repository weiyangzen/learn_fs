# File Research: sources/os/plan9/9front/sys/src/9/imx8/gpc.c

Role: i.MX8 power gating controller helper for powering up named power domains.

Key responsibilities:
- Defines GPC power-up/down request and CPU mapping registers.
- Maps domain names such as `mipi`, `pcie`, `usb_otg1`, `gpu`, `vpu`, `hdmi`, `disp`, and `pcie2` to request bits.
- `powerup()` matches a name case-insensitively, temporarily maps PGCs to CPUs, sets the PUP request bit, waits until hardware clears it, then clears CPU mapping.

Dependencies:
- Hard-wired GPC MMIO at `VIRTIO + 0x3A0000`.
- Used by LCD, USB, and PCIe initialization.

Notes:
- Unknown domain names panic.
- There is no public power-down helper in this file.
