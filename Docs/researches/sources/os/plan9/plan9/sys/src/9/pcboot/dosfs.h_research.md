# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dosfs.h

## Purpose
Shared FAT boot filesystem structures, partition constants, and `Bootfs` abstraction declarations.

## Main Interfaces
- Defines `Dospart`, `Dosfile`, `Dos`, `Dosboot`, `Dosdir`, `File`, and `Bootfs`.
- Declares `fsread`, `fsboot`, `fswalk`, and `dosinit`.
- Defines FAT partition type constants and DOS attribute bits.

## Implementation Notes
- `Bootfs` embeds `Dos` as its first union member, allowing casts between `Dos*` and `Bootfs*` in `dosboot.c`.
- `File` contains a union currently used for `Dosfile`.
- `Bootfs` can either use a device channel or callback-style disk read/seek functions used by BIOS backends.
- Defines `BADPTR(x)` for simple high-kernel-address validation.

## Dependencies And Risks
- Structure layout coupling is intentional and fragile; `Dos` must stay at the start of `Bootfs`.
- FAT32 fields are present in `Dosboot` but only needed subset is consumed by `dosboot.c`.
