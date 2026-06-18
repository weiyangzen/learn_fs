# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeas.sh

Generator script for m68060 FPLSP wrapper assembly. It creates dummy files, double and float wrapper files, `fplsp_wrap.S`, and `Makefile.list` from a fixed table of FPLSP offsets.

The wrappers adapt SVR4 and non-SVR4 m68k calling conventions and generate weak aliases for public math names.
