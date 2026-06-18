# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/Makefile

Helper makefile for generating m68060 libm wrapper sources. It builds `fplsp.hex` from Motorola FPSP input, runs `makeoffs.awk`, uses `makeas.sh` to regenerate wrapper assembly and `Makefile.list`, and cleans generated artifacts.
