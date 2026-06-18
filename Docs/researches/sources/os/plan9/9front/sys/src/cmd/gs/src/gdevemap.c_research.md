# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevemap.c

## Role
`gdevemap.c` provides static mapping tables between PostScript StandardEncoding and ISO Latin-1 encoding.

## Contents
- Defines `const byte gs_map_std_to_iso[256]`.
- Defines `const byte gs_map_iso_to_std[256]`.
- Includes only `std.h`.

## Behavior
- No functions or dynamic state.
- Entries with no mapping are represented as `0`.

## Risks and Notes
- Data-only utility file. No filesystem, device I/O, memory allocation, or external process interaction.
