# File Research: sources/os/plan9/9front/sys/src/9/bcm64/sdhc.c

BCM2711 SDHCI/eMMC2 host-controller driver with ADMA2 support.

Key responsibilities:
- Registers `SDio` controller named `sdhc`.
- Maps SDHCI registers at `VIRTIO+0x340000`.
- Initializes/reset host controller and sets bus power/voltage.
- Sets SD clock and bus width.
- Builds ADMA2 descriptors for data transfers.
- Issues SD commands, parses response formats, handles busy responses, and waits for command/data completion.
- Handles data setup, DMA cache maintenance, and interrupt wakeups.

Important behavior:
- Uses mailbox `ClkEmmc2`, with a 100 MHz fallback if missing.
- Allows `*emmc2bus` override for bus-visible DRAM address base.
- Resets command/data circuits when inhibit bits get stuck.
- Masks card and DMA interrupts out of normal data wait handling.

Dependencies:
- Plan 9 SD core, cache/DMA helpers, BCM clock mailbox, interrupt controller, and SoC bus-DRAM mapping.
