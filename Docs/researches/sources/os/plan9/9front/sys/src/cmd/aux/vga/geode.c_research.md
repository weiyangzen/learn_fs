# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/geode.c

Implements AMD Geode display controller setup using PCI MMIO plus MSR clock programming. `snarf` finds device `1022:2081`, attaches `geodemmio`, saves display-controller registers and clock MSR `0x4C000015`, and records a few VGA CRTC extension values.

`init` chooses low- or average-bandwidth preset registers by width, enables FIFO/display/timing/palette bypass, sets display mode by bpp, programs horizontal/vertical timing registers, line pitch, framebuffer active size, and looks up the exact pixel clock in `geode_modes.h`.

`load` writes the selected clock MSR, unlocks the display controller, and programs timing/config registers. `geodehwgc` is an empty placeholder.
