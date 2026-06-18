# File Research: sources/os/plan9/plan9/sys/src/9/pc/pcmciamodem.c

PCMCIA modem auto-link helper for known modem card names.

Key elements:
- Lists known modem product strings, including IBM, Xircom, Motorola, Sierra/Novatel/Psion style cards.
- `pcmciamodemlink` searches `serialN=type=com` ISA config lines for explicit port/IRQ settings.
- Defaults first unconfigured card to COM2, port `0x2f8`, IRQ 3.
- Calls `pcmspecial` to bind a matching PCMCIA card to the ISA serial configuration.
- Reserves I/O space with `ioalloc` and prints discovered slot/port/IRQ.

Interactions:
- Depends on PCMCIA support and serial/i8250 setup elsewhere.
- Uses Plan 9 ISA configuration parsing.

Research notes:
- Peripheral convenience support only.
- No filesystem relevance except enabling modem devices as system I/O.
