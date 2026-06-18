# sources/user-network-fs/libsmb2/include/portable-endian.h

## Purpose
`portable-endian.h` normalizes host-to/from big/little endian conversion macros across many operating systems, consoles, and embedded targets used by libsmb2.

## Important APIs, Types, and Functions
It defines or maps `htobe16`, `htole16`, `be16toh`, `le16toh`, and 32/64-bit variants. Platform branches cover PS2/Pico, Dreamcast, Linux/Cygwin/ESP/BSD/GNU, Apple, PS3/Wii/GameCube, Switch/3DS/NDS, Windows/Xbox, Amiga, AROS, and generic GCC/Clang. Some branches define `__BYTE_ORDER`, `__BIG_ENDIAN`, and related aliases.

## Control Flow
Preprocessor conditionals select exactly one platform branch at compile time. There is no runtime branch; conversions are macros wrapping system functions, builtin byte swaps, or identity operations depending on host endian.

## State and Persistence Behavior
No state is stored. The header determines binary wire-format correctness for all SMB2/DCERPC scalar encoding.

## Dependencies and Integration Points
It integrates with packers/unpackers that read/write SMB2's little-endian fields and with network byte-order helpers for some embedded targets. It includes platform headers such as `<endian.h>`, `<sys/endian.h>`, `<libkern/OSByteOrder.h>`, `<windows.h>`, `<xtl.h>`, or `<machine/endian.h>`.

## Risks and Edge Cases
The PS2/Pico branch maps 64-bit big-endian conversion as `htobe64(x) be64toh(x)` but does not visibly define `be64toh` in that branch, relying on included platform support. Generic GCC/Clang assumes little-endian identity for `htole*`; unusual big-endian GCC targets must hit an earlier branch. Macro redefinitions can conflict with system headers.

## Test Signals
Compile on each supported platform branch when possible and run encode/decode round trips for 16/32/64-bit values, including SMB headers and DCERPC NDR scalars.
