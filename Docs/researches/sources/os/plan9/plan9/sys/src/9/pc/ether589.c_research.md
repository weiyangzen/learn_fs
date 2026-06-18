# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether589.c

Read completely: 215 lines.

This file implements PCMCIA 3Com 3C589/3C562 Ethernet setup, delegating final operation to the existing EtherLink III driver.

Key behavior:
- Looks for PCMCIA cards whose version string matches `3C589`, `3C562`, or `589E`.
- Claims cards through `pcmspecial()`.
- Configures 3Com ASIC register windows, IRQ routing, transceiver selection, TX/RX reset, and media.
- For 3C562, reads the Ethernet address from tuple `0x88` if the address was not overridden.
- Allows `media=10base2` or `media=10baseT`.
- Falls back from 10BaseT to 10Base2 when autoselect is allowed and link beat is absent.

Important interfaces:
- Link function: `ether589link()`.
- Calls external `etherelnk3reset(Ether*)`.
- Uses `pcmspecial()`, `pcmcistuple()`, and `pcmspecialclose()`.

Research notes:
- Comments state IRQ must be 3 on 3C589/3C562, though the reset function defaults `ether->irq` to 10 before PCMCIA configuration.
- The driver is mostly a PCMCIA/Card Services adapter for the shared 3Com driver.
