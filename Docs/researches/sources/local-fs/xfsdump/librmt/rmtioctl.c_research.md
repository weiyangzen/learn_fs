# File Research: sources/local-fs/xfsdump/librmt/rmtioctl.c

Implements local/remote tape `ioctl` support, mainly `MTIOCTOP` and `MTIOCGET`.

Core behavior:
- Local descriptors call `ioctl(2)`.
- Remote `MTIOCTOP` maps Linux tape op codes to IRIX or fallback standard op codes when needed, sends `I<op>\n<count>\n`, and returns remote status.
- Remote `MTIOCGET` sends `S`, reads binary tape status, interprets it as IRIX, Linux 32-bit, or Linux 64-bit layout based on detected remote host and returned size.
- Performs heuristic byte swapping if fields look byte-swapped.
- Converts IRIX status bits into Linux `GMT_*` generic status bits.

Dependencies:
- Remote host type is set by `rmtopen()` via remote `uname`.
- Uses `swap.h` macros for integer byte swapping.
- Uses Linux `<sys/mtio.h>` structures and constants.

Risks/assumptions:
- Supports only known Linux and IRIX status layouts.
- `mtop_*map` arrays are size `MT_MAX`; incoming `mt_op` values are used as indexes without explicit bounds checks.
- Binary protocol remains architecture-sensitive despite conversion logic.
