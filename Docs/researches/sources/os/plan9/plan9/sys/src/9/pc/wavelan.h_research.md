# File Research: sources/os/plan9/plan9/sys/src/9/pc/wavelan.h

## Purpose
Shared constants, Hermes register definitions, frame/LTV/stat structures, controller state, and function prototypes for the WaveLAN driver family.

## Main Interfaces
- Defines LTV type constants such as `WTyp_Stats`, `WTyp_Scan`, `WTyp_Mac`, `WTyp_NetName`, `WTyp_Crypt`, `WTyp_Keys`.
- Defines Hermes CSR registers and event bits: `WR_Cmd`, `WR_EvSts`, `WR_IntEna`, `WEvs`, etc.
- Defines frame constants for 802.11/802.3 offsets and SNAP encapsulation.
- Defines `WStats`, `WScan`, `WFrame`, `WKey`, `Wltv`, `Stats`, and `Ctlr`.
- Declares public driver routines implemented by `wavelan.c`.

## Implementation Notes
- `Ctlr` embeds a `Lock`, configuration state, transmit buffers, WEP key data, PCI/MMIO fields, and both software and card-provided stats.
- Default radio settings include managed mode, AP density, RTS threshold disabled at `2347`, and automatic transmit rate.
- WEP supports four keys with 5-13 byte valid key lengths and a 14-byte stored key slot.
- `Wltv` is a compact union matching the card’s length-type-value control records.

## Dependencies And Risks
- Layouts are hardware ABI structures; padding and endianness are important.
- `BADPTR`-style validation is not here; callers assume the shared layout matches card command payloads.
