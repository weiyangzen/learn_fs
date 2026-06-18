# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/data.c

Defines global aux/vga state and the controller registry. `cflag` disables hardware cursor use; `dflag` controls palette behavior.

`ctlrs[]` is the central dispatch table of all supported VGA controllers, RAMDACs, clocks, VESA paths, and hardware cursor modules. The files in this group contribute entries such as `bt485`, `ch9294`, `clgd542x`, `igfx`, `mach64xx`, and `mga2164w`.

`dacxreg[4]` maps low two indirect DAC address bits onto VGA palette/mask register ports, used by RAMDAC implementations such as `bt485`.
