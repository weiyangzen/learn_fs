# File Research: sources/os/bsd/dragonflybsd/sys/sys/gmon.h

`gmon.h` defines profiling data structures used for `gmon.out`/`monstartup()` style profiling. It includes `machine/profile.h`.

It defines `struct gmonhdr`, `GMONVERSION`, histogram counter type, histogram/hash allocation fractions, arc density limits, `struct tostruct`, raw arc records, rounding macros, and `struct gmonparam`, which stores histogram, from/to arc tables, text range, profiling rate, overhead counters, and state.

It declares global `_gmonparam`, profiling state constants, and user-visible `moncontrol()` and `monstartup()`.
