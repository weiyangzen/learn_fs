# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/cdc.c

This file implements generic CDC Ethernet packet framing for the nusb Ethernet server. It uses no device-specific data headers: `cdcreceive()` reads a USB bulk packet directly into a `Block` and submits it to `etheriq()`, and `cdctransmit()` writes the Ethernet frame as-is.

The transmit path sends a zero-length packet when the frame length is an exact multiple of the endpoint max packet size, with a comment noting that some Linux behavior differs by sending an extra byte.

`cdcinit()` scans device-specific descriptors for an Ethernet networking functional descriptor (`Dfunction`, `Fnether`). It loads the MAC-address string referenced by the descriptor, validates that it is 12 hex characters, parses it into `macaddr`, and installs receive/transmit callbacks. It returns failure if no suitable descriptor/MAC is present.
