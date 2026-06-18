# File Research: sources/os/plan9/9front/sys/src/9/bcm64/sdhost.c

BCM2835 SDHOST controller driver using the platform DMA engine.

Key responsibilities:
- Registers `SDio` controller named `sdhost`.
- Maps SDHOST registers at `VIRTIO+0x202000`.
- Initializes power, command, status, clock divisor, block size/count, and host config.
- Sets bus width and SD clock.
- Sends SD commands and returns short/long responses.
- Transfers data through `dmastart()`/`dmawait()` using `DmaChanSdhost`.

Important behavior:
- Reports host status errors through generated error strings.
- Uses a 500 ms timeout counter derived from the selected clock.
- LED hook drives the platform `okay()` indicator.

Dependencies:
- Plan 9 SD core, BCM DMA helpers, clock mailbox, and GPIO/LED support.
