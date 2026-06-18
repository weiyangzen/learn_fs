# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devether.c

One-line reuse shim including `../omap/devether.c`.

The BCM port reuses the OMAP generic Ethernet device framework. BCM-specific Ethernet discovery is provided by `archether()` in `archbcm.c` and USB Ethernet proxy support in `etherusb.c`.
