# File Research: sources/os/plan9/9front/sys/src/9/pc/etherec2t.c

PCMCIA NE2000/DP8390 clone driver for Linksys/Accton/Netgear/SMC cards, registered as `EC2T`.

Primary role:
- Board-specific wrapper around the shared `ether8390.c` DP8390 core for several PCMCIA Ethernet cards.

Supported card names:
- `EC2T`, `PCMPC100`, `PCM100`, `EN2216`, `FA410TX`, `FA411`, `Network Everywhere`, `10/100 Port Attached`, `8041TX-10/100-PC-Card-V2`, `SMC8022`.
- Also supports user option `id=<name>` and optional `iochecksum`.

Important behavior:
- `reset()` applies defaults when unspecified: port `0x300`, IRQ `9`, adapter memory offset `0x4000`, size `16*1024`.
- Allocates I/O range `0x20`, asks PCMCIA layer for a matching special card, allocates and fills `Dp8390`.
- Configures DP8390 as 16-bit remote-DMA I/O (`width = 2`, `ram = 0`, `data = port + 0x10`).
- Computes TX/RX ring pages from `ether->mem`, Ethernet packet size, and card memory size.
- Resets board by reading and writing reset port offset `0x1F`.
- Calls `dp8390reset()` before probing PROM/address data.
- For checksum-style cards, reads eight bytes from I/O space at `port + 0x14` and requires sum `0xFF`.
- For PROM-style cards, reads first 16 words via `dp8390read()` and requires marker bytes `0x57, 0x57`.
- If station address is not preconfigured, copies bytes from the PROM/checksum buffer, then calls `dp8390setea()`.

Research notes:
- On probe failure after PCMCIA open, it closes the special slot, frees I/O, and frees controller state.
- This file relies heavily on `ether8390.h`/`ether8390.c` for all packet I/O after board setup.
