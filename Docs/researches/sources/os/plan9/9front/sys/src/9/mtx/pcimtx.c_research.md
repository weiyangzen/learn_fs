# File Research: sources/os/plan9/9front/sys/src/9/mtx/pcimtx.c

This file implements PCI configuration-space access and bus scanning setup for MTX. It detects PCI configuration mechanism 1 or 2, sets maximum bus/device limits from configuration if present, scans buses with portable PCI helpers, resets CardBus bridges found on bus 0, computes and applies PCI bus resource mappings, and exposes `pcimtxlink`.

`pcicfgrw8`, `pcicfgrw16`, and `pcicfgrw32` implement read/write access for both PCI config mechanisms using `0xCF8/0xCFC` or mode-2 ports.

Filesystem relevance is indirect through PCI storage, network, and other device drivers. The Ethernet driver in this group depends on PCI discovery and config access here.

Notable risks: PCI mapping starts with fixed `ioa=0x1000` and `mema=0`; mode-2 support is retained despite being deprecated; behavior depends on portable PCI helpers outside this file.
