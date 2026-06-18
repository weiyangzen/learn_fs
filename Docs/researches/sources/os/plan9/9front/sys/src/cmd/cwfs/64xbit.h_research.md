# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/64xbit.h

Extended-name 64-bit cwfs layout variant.

Important details:
- `NAMELEN=144`, `NDBLOCK=6`, `NIBLOCK=4`.
- `Off` is `vlong`.
- Undefines `COMPAT32`.
- `swaboff` maps to `swab8`.
- It trades compatibility for much longer directory component names.
