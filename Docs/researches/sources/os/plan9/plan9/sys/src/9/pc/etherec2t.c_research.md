# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherec2t.c

## Role

Plan 9 PCMCIA wrapper driver for NE2000-like Ethernet cards, including Linksys, Accton, Netgear, SMC, and related cards. It uses the shared DP8390 core from `ether8390.c`.

## Main Interfaces

- `etherec2tlink()` registers `addethercard("EC2T", reset)`.
- `reset()` probes/configures a matching PCMCIA card and then delegates common NIC setup to `dp8390reset` and `dp8390setea`.

## Data Structures

- `Ec2t`: PCMCIA product-name matcher plus flag indicating whether MAC address/checksum are read from I/O space.
- `ec2tpcmcia[]`: supported card name table.
- Uses `Dp8390` from `ether8390.h`.

## Important Behavior

- Supplies default port `0x300`, IRQ `9`, memory offset `0x4000`, and size `16 KiB` when not configured.
- Allocates the I/O range and finds a matching PCMCIA special entry, with optional `id=` override and `iochecksum` option.
- Initializes `Dp8390` for 16-bit I/O, no shared memory, data port at base + `0x10`.
- Computes transmit and receive page layout from `ether->mem`, `ether->size`, and `Dp8390BufSz`.
- Resets board by reading and writing the reset port.
- Validates card identity either by I/O-space checksum or by reading PROM marker bytes through DP8390 remote DMA.
- Loads MAC address from PROM/I/O bytes unless user supplied one, then writes it to the DP8390 core.

## Dependencies And Assumptions

- Depends on PCMCIA helper `pcmspecial`, `pcmspecialclose`, and the shared DP8390 implementation.
- Assumes NE2000-compatible register layout with data port offset `0x10` and reset port offset `0x1F`.
- Assumes 16-bit transfers.

## Notable Risks

- If `malloc(sizeof(Dp8390))` succeeds but later validation fails, cleanup frees controller memory but does not clear `ether->ctlr`.
- Probe identity relies on product strings and weak PROM/checksum signatures.
- Default I/O/IRQ settings may conflict unless overridden by configuration.
