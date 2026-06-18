# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/64bit.h

64-bit cwfs on-disk layout constants.

Important details:
- `NAMELEN=56`, `NDBLOCK=6`, `NIBLOCK=4`.
- `Off` is `vlong`.
- Undefines `COMPAT32`.
- `swaboff` maps to `swab8`.
- This layout is intentionally incompatible with old 32-bit filesystems.
