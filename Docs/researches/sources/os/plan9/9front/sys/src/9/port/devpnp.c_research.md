# File Research: sources/os/plan9/9front/sys/src/9/port/devpnp.c

Purpose: Implements `#$` for ISA Plug-and-Play discovery plus PCI configuration-space access.

Key logic:
- ISA PNP support sends the initiation key, runs serial isolation, assigns CSNs, reads resource data, and exposes `csnNctl`/`csnNraw`.
- Boot-time `pnpN=` configuration strings can predefine card IDs and optional config strings before scanning.
- `pnp/ctl` reports enabled/disabled state and accepts `port` to scan an ISA PNP read-data port plus `debug`.
- PCI directory support mirrors `devpci.c`: per-device `ctl` summaries and `raw` 256-byte config-space access.
- `QID` packs card/device identity and file type; `CSN` extracts ISA card numbers.

Dependencies and integration:
- Uses low-level I/O port access (`inb`, `outb`), ISA config parsing, PCI helpers, and Plan 9 directory generation.

Risks and notes:
- ISA PNP resource configuration is stubbed through `wrconfig`, which currently accepts commands without implementing real resource programming.
- PCI raw writes are direct hardware config writes.
- The file mixes old ISA PNP hardware probing with generic PCI config exposure.
