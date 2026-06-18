# File Research: sources/os/linux/linux/fs/afs/protocol_uae.h

## Purpose
Defines Universal AFS Error (UAE) abort code constants.

## Main Responsibilities
- Provides a contiguous enum of UAE error codes starting at `0x2f6df00`.
- Mirrors many Unix/Linux errno meanings into AFS protocol abort namespace constants.
- Supplies constants consumed by error translation in `misc.c`.

## Key Content
- Basic filesystem/process errors: `UAEPERM`, `UAENOENT`, `UAEIO`, `UAEACCES`, `UAEBUSY`, `UAEEXIST`, `UAENOTDIR`, `UAEISDIR`.
- Filesystem limit/state errors: `UAEFBIG`, `UAENOSPC`, `UAEROFS`, `UAEMLINK`, `UAENAMETOOLONG`, `UAENOTEMPTY`, `UAEOVERFLOW`, `UAEDQUOT`, `UAENOMEDIUM`.
- Network/socket errors: `UAENETUNREACH`, `UAECONNABORTED`, `UAECONNRESET`, `UAETIMEDOUT`, `UAECONNREFUSED`, `UAEHOSTDOWN`, `UAEHOSTUNREACH`.
- Miscellaneous protocol/system errors through `UAEMEDIUMTYPE`.

## Important Details
- `misc.c` maps only selected UAE constants to Linux errno; unmapped abort codes fall back through the default remote I/O path.
- The file is protocol data only and contains no functions or include guards in the visible content.
