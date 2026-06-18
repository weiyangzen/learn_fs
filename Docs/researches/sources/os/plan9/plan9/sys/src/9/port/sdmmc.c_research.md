# File Research: sources/os/plan9/plan9/sys/src/9/port/sdmmc.c

Implements an `sd` interface for a single MMC/SD memory card over a platform-provided `SDio` host controller.

Key responsibilities:
- `mmcpnp` initializes the `sdio` host and creates one `SDev`/`Ctlr`.
- `mmcverify` fills basic inquiry data using `SDio.inquiry`.
- `mmcenable` invokes the host enable hook.
- `mmconline` initializes the card: idle, SD 2.0 voltage check, operating-condition polling, CID/RCA/CSD reads, capacity identification, card select, block length, and 4-bit bus width.
- `identify` decodes CSD v1/v2 capacity and sector size, normalizing 1024-byte sectors to 512-byte sectors.
- `mmcrctl` reports RCA/OCR/CID/CSD and geometry.
- `mmcbio` performs block reads/writes through `SDio.iosetup`, `SDio.cmd`, and `SDio.io`, using multi-block commands when enabled.
- `mmcrio` is a stub returning `-1`.

Important behavior:
- SDHC/SDXC addressing is selected via OCR `Ccs`: block number for high-capacity cards, byte offset for older cards.
- Multi-block I/O retries setup errors up to three times and sends `STOP_TRANSMISSION`.
- Assumes exactly one card on the bus.

Role:
- Portable MMC/SD storage bridge into the generic `sd` framework.
