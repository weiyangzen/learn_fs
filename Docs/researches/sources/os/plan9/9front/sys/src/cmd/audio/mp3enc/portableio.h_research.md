# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.h

## Scope
Header for portable endian/file I/O routines.

## APIs
Declares byte, 16/24/32-bit integer, raw byte, swapped byte, IEEE float/double, and IEEE extended read/write helpers. Defines C/C++ linkage macro `CLINK`, `Read32BitsLowHigh(f)` as `Read32Bits(f)`, and `WriteString(f,s)` as an `fwrite` wrapper.

## Dependencies
Includes `stdio.h`.

## Risks and Notes
The header exposes APIs whose implementations may be absent or compiled elsewhere. `WriteString` uses `strlen` but this header does not include `string.h`, so includers must provide it.
