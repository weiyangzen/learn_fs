# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.h

## Role

Shared definitions for MGR bitmap output devices.

## Main Contents

- Declares MGR 8-bit color mapping procedures.
- Defines `struct b_header` and `B_PUTHDR8` for MGR saved bitmap headers.
- Defines `struct nclut` lookup-table entries.
- Defines MGR palette constants and six 16-entry LUT families: black/white, gray, bit-reordered gray, VGA, BCT, and user.
- Provides a static `mgrlut[LUT][RGB][LUTENTRIES]` table.

## Design Notes

The header embeds static palette data directly, so every C translation unit including it gets its own `mgrlut`. In this group it is used by `gdevmgr.c`.

## Research Notes

Format-support header only; no filesystem behavior.
