# File Research: sources/os/plan9/9front/sys/src/9/bcm/ether4330.c

Broadcom BCM4330-family SDIO Wi-Fi Ethernet driver.

Key behavior:
- Takes over the eMMC SDIO bus, reconfigures GPIO routing to Wi-Fi pins, negotiates SDIO functions, high speed, 4-bit bus, and block sizes.
- Implements SDIO direct and extended I/O, backplane windowing, chip memory/register access, packet I/O, and abort/reset paths.
- Scans Silicon Backplane cores, detects supported chip IDs/revisions, resets ARM/D11/SOCRAM cores, sizes RAM, and configures clocks/pulls/drive strength.
- Selects firmware/config/regulatory files by chip ID/revision, uploads firmware/config into chip RAM, verifies uploads, and releases the on-chip ARM core.
- Implements SDPCM framing for command, event, and data channels.
- Runs reader and timer kernel processes for packet/event reception and periodic scanning.
- Implements firmware command interface, variables, WEP/WPA/WPA2 keys, join, scan, event handling, link state, multicast/promiscuous mode, and ifstat output.
- Registers an Ethernet card named `4330`.

Dependencies:
- Uses SDIO, Ether, netif, GPIO, firmware files in `/boot` or `/lib/firmware`, block queues, and Plan 9 command parsing.

Research notes:
- The driver supports multiple related Broadcom chips, including 4330, 43362, 43430, and 4345 variants.
- The control interface is tailored for `aux/wpa` expectations, including status strings and key commands.
