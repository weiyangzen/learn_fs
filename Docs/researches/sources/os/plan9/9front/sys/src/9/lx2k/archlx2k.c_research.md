# File Research: sources/os/plan9/9front/sys/src/9/lx2k/archlx2k.c

Minimal LX2K architecture hook. It disables the ARM SBSA watchdog by writing zero to the watchdog control/status register at `VIRTIO+0x13a0000`.

`archlx2klink` performs this watchdog shutdown during platform link/setup.

Notable risks: the watchdog address is hard-coded and there is no validation or status readback.
