# File Research: sources/os/plan9/9front/sys/src/cmd/ki/symbols.c

Symbol/source helpers for `ki` debugger output. `printsource` maps a PC to file:line text. `printlocals` and `printparams` use Plan 9 symbol APIs to locate auto variables and parameters and read their values from simulated stack memory.

`stktrace` walks SPARC stack frames from current `pc` and `sp`, using `.frame` local metadata and saved return PCs. It prints function names, parameters, source locations, callers, and optionally locals for `$C`, truncating after 40 frames. This file bridges the simulator’s memory model and libmach symbols.
