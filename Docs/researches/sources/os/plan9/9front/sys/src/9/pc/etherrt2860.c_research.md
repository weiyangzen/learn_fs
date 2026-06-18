# File Research: sources/os/plan9/9front/sys/src/9/pc/etherrt2860.c

Implements a Plan 9 Wi-Fi/Ethernet driver for Ralink RT2860-family PCI/PCIe wireless devices, especially RT2790 and RT3090.

Key behavior:
- Defines extensive PCI, DMA, PBF, MAC, BBP, RF, EEPROM/eFUSE, security table, TXWI/RXWI, and descriptor constants.
- Maintains controller state for MAC/RF revision, RF chains, EEPROM calibration data, per-channel TX power, RSSI/LNA offsets, WCID slots, RX/TX rings, firmware image, and Wi-Fi integration.
- Reads firmware `ral-rt2860` from `/boot` or `/lib/firmware`, uploads it to MCU program RAM, and waits for MCU readiness.
- Uses MCU mailbox commands for BBP access, LEDs, RF reset, sleep/wakeup, and PCIe power-save settings.
- Reads calibration and identity data from serial EEPROM or RT3071+ eFUSE, including MAC address, RF type, chain counts, BBP/RF overrides, power tables, LNA/RSSI, LEDs, and power-save level.
- Initializes MAC defaults, BBP defaults, EEPROM BBP overrides, RF programming, RT3090 filter calibration, antenna selection, DMA rings, WCID/key tables, RX filters, protection, RTS threshold, and LEDs.
- Supports channel changes through classic RT2860 RF register programming or RT3090-style RF CSR programming.
- Integrates with `wifiattach`; `transmit` builds TXWI plus 802.11 header descriptors, assigns WCID for broadcast/BSS, queues EDCA TX, and hardcodes basic rates.
- RX interrupt path drains descriptors, handles RXWI, optional L2 padding, CRC/ICV drops, and passes frames to `wifiiq`.
- TX interrupt path frees DMA payload blocks, clears descriptors, and reads TX status FIFO.
- Promiscuous mode updates Wi-Fi RX state and hardware receive filters; multicast callback is empty.

Dependencies:
- Uses Plan 9 PCI, Ether, Wi-Fi layer (`wifi.h`), firmware file I/O, DMA, block allocation, interrupts, and kernel locking.
- Based on behavior from OpenBSD `ral(4)` per file header.

Research notes:
- Attach requires privileged firmware access via `iseve`.
- PCI probe only accepts Ralink vendor `0x1814` and devices RT2790/RT3090, despite broader constants and code paths.
- Management queue uses EDCA AC VO for RT2860C because the hardware management ring is noted as broken.
- Many 802.11 capabilities are minimal or fixed: basic rate handling is simple, multicast is unimplemented, and some calibration flags are disabled with `XXX` comments.
