# File Research: sources/os/plan9/9front/sys/src/9/ppc/io.h

PowerPC bus-number encoding definitions.

Key responsibilities:
- Enumerates bus type IDs used in TBDF encodings.
- Defines `MKBUS()` and helper macros for bus/function/device/type extraction.
- Defines `BUSUNKNOWN`.

Dependencies:
- Used by device and bus code needing Plan 9 TBDF-style identifiers.
