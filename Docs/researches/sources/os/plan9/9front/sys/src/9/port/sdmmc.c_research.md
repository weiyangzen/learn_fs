# File Research: sources/os/plan9/9front/sys/src/9/port/sdmmc.c

Generic MMC/SD card backend over registered `SDio` host controllers.

Key responsibilities:
- Defines common MMC/SD command descriptors.
- Registers SDio host controllers with `addmmcio()` and enumerates them through `mmcpnp()`.
- Allocates `SDev`/`Card`/host-controller copies, supports annexing a controller, and clears controllers.
- Initializes cards by trying SD first, then MMC, reading OCR/CID/CSD/EXT_CSD as appropriate.
- Parses CSD/EXT_CSD to determine card version, sector size, total user sectors, and MMC boot areas.
- Selects card, sets block length, switches bus speed and width, and attempts high-speed modes.
- Implements retry kproc after online/init failures.
- Exposes card status through `rctl`.
- Implements single- and multi-block reads/writes through host `iosetup`, `cmd`, and `io`.
- Switches MMC boot partition selection based on unit subnumber.
- Provides fake SCSI request handling through `mmcrio()`.

Important behavior:
- `Card.sectors[0..2]` represent user and boot areas.
- SD high-capacity cards use block addressing when OCR `Ccs` is set; otherwise byte addressing is used.
- MMC 4.0+ cards attempt high-speed timing and 8-bit/4-bit/1-bit bus width fallback.
- Multi-block write is disabled if host has `nomultiwrite`.
- LED callbacks are toggled around data transfers when available.

Notable risks:
- Retry handling uses a background kproc and `card->retry` coordination; clear/free waits for it by repeatedly locking.
- Many command sequences are hardware timing-sensitive and use sleeps between bus/card state changes.
