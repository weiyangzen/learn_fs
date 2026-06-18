# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.spim.h

SPIM Ghostscript architecture override. It includes `default.mips.h`, then undefines and resets `ARCH_IS_BIG_ENDIAN` to `0`, making SPIM use MIPS defaults except little-endian byte order.
