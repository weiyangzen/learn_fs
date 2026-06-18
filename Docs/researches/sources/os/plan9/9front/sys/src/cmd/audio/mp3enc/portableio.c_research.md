# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.c

## Scope
Endian-independent file I/O helpers for integer and extended floating-point values, originally from Apple/Slaney/Turkowski code.

## APIs and Behavior
Implements `ReadByte`, 16/24/32-bit low-high and high-low readers, 8/16/32-bit writers, byte-block read/write with optional byte reversal, `ConvertFromIeeeExtended`, and `ReadIeeeExtendedHighLow`. Some alternate implementations are compiled under `KLEMM_36`.

## Dependencies
Uses `stdio.h`, `math.h` or `ymath.h`, and `portableio.h`.

## Risks and Notes
The file’s own comments call out portability flaws: assumes 8-bit chars, does not handle EOF robustly, assumes 32-bit-or-larger `int`, and lacks write error checks. Several functions mask `getc()` without checking EOF first. `portableio.h` declares more IEEE float/double read/write APIs than this file visibly implements.
