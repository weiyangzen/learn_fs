# File Research: sources/os/plan9/9front/sys/src/9/pc/pcmciamodem.c

Small PCMCIA modem autodetection/link helper.

Key behavior:
- Contains a static list of modem CIS/product strings, including IBM, Xircom, Motorola, Sierra/Novatel/Psion-style cellular modem names.
- `pcmciamodemlink()` walks known modem names and available `serialN=type=com` ISA configuration entries.
- If no explicit serial config is found and COM2 has not already been assigned, it defaults the first found modem to IRQ 3 and port `0x2F8`.
- Calls `pcmspecial()` to bind a matching PCMCIA card to the chosen `ISAConf`.
- Reserves the serial I/O port with `ioalloc()` and prints the detected slot, port, and IRQ.

Research notes:
- This is legacy laptop/modem support, not filesystem or storage code.
- The loop deliberately avoids assigning default COM2 to more than one modem.
- It assumes a laptop with PCMCIA usually has only one COM port unless plan9.ini supplies explicit serial configuration.
