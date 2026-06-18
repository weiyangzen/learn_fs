# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgax.c

## Purpose
Shared locked helpers for reading and writing VGA indexed registers.

## Main Interfaces
- Exports `vgaxi(long port, uchar index)` for indexed register reads.
- Exports `vgaxo(long port, uchar index, uchar data)` for indexed register writes.

## Implementation Notes
- Serializes access through static `Lock vgaxlock`.
- Supports sequencer, CRT controller, graphics controller, and attribute controller indexed ports.
- Attribute controller access resets flip-flop by reading `Status1`, handles palette indices below `0x10`, and restores display-enable bit `0x20`.
- For standard indexed registers it writes index to `port` and reads/writes `port+1`.

## Dependencies And Risks
- Returns `-1` for unsupported ports despite return type `int`; callers expecting unsigned byte data must handle this.
- Attribute controller sequencing is hardware-sensitive and intentionally conservative.
