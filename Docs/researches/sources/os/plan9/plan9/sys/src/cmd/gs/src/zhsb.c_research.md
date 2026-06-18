# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zhsb.c

HSB color operator glue. `currenthsbcolor` calls `gs_currenthsbcolor` and pushes hue, saturation, and brightness. `sethsbcolor` reads three numeric operands, calls `gs_sethsbcolor`, clears the interpreter cached color-space array reference, and pops the operands.

The file registers only `currenthsbcolor` and `sethsbcolor`. It is a thin bridge from PostScript operands to the graphics library’s HSB conversion/state routines.
