# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arch.c

This is a one-line platform reuse shim: it includes `../omap/arch.c`.

The BCM port delegates generic ARM architecture support to the OMAP implementation and keeps BCM-specific reset/watchdog/Ethernet architecture hooks in `archbcm.c`.

There is no local logic, state, or API surface beyond the included file.
