# File Research: sources/os/plan9/9front/sys/src/9/bcm/gpio.c

Low-level Raspberry Pi GPIO register operations.

Key behavior:
- Maps GPIO registers at `VIRTIO + 0x200000`.
- Sets pin function select fields.
- Configures pull-up/down/off using legacy BCM2835-2837 handshake or BCM2711 pull registers.
- Sets, clears, and reads pin levels.
- Enables/disables rising or falling edge detection and reads/clears event status.
- Registers the GPIO MMIO page as a physical device segment.

Dependencies:
- Uses SoC physical/virtual mapping, `addphysseg`, and delay helpers.

Research notes:
- `gpiomeminit` exposes GPIO as a device physical segment named `gpio`.
