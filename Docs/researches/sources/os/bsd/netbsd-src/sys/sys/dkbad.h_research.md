# File Research: sources/os/bsd/netbsd-src/sys/sys/dkbad.h

Defines DEC STD 144 bad-sector table layout and related constants.

Key content:
- `NBT_BAD` maximum of 126 bad sectors.
- `struct dkbad` with cartridge serial, flags, and `bt_bad` array of cylinder/track-sector pairs.
- `HAS_BAD144_HANDLING` capability marker.
- Error constants: `ECC`, `SSE`, `BSE`, `CONT`.
- Kernel `isbad` prototype.

Important behavior:
- Comments describe storage in the first five even-numbered sectors of the last track and replacement-sector allocation rules.
- Legacy disk bad-block remapping support.
