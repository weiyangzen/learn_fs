# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/64bit.h

cwfs 64-bit on-disk layout constants.

It sets `NAMELEN` to 56, `NDBLOCK` to 6, `NIBLOCK` to 4, and defines `Off` as `vlong`, creating an incompatible 64-bit filesystem format. The comment notes the name length choice keeps three dentries per magnetic disk sector.

It undefines `COMPAT32` and maps `swaboff` to `swab8`.
