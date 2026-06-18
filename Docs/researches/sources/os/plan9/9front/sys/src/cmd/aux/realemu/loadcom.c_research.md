# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/loadcom.c

`loadcom` loads a DOS `.COM` program into Plan 9 real-mode execution devices. It opens the input file, `/dev/realmode`, and `/dev/realmodemem`, reads up to 0xFF01 bytes, writes the program at `CS:0100`, and writes an initialized `/386/include/ureg.h` register image.

It sets CS/DS/ES/FS/GS to `0x1000`, SS to `0`, SP to `0xfffe`, and PC to `0x0100`. It is a thin helper for bootstrapping real-mode code through the realmode device interface.
