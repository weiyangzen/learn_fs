# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode_modes.h

Contains `NumModes = 61` and a static `geode_modes` lookup table mapping Geode clock MSR selector words to exact pixel-clock frequencies.

`geode.c` requires an exact frequency match in this table; unknown mode clocks are rejected rather than approximated. The table spans common VGA through high-resolution pixel clocks from about 24.923 MHz to 341.349 MHz.
