# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/32bit.h

On-disk layout constants for old 32-bit-compatible cwfs builds.

Important details:
- `NAMELEN=28`, `NDBLOCK=6`, `NIBLOCK=2`.
- `Off` is `long`.
- Defines `COMPAT32`.
- `swaboff` maps to `swab4`.
- Comments warn that changing these values breaks disk compatibility and 9P1 compatibility.
