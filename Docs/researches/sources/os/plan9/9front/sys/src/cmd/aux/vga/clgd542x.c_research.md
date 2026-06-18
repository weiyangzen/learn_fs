# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/clgd542x.c

Implements Cirrus Logic CL-GD542x/543x-style VGA controller setup. It unlocks extended sequencer registers, snarfs extended sequencer/graphics/CRT registers, reads the hidden DAC register, identifies chip IDs, and determines memory size plus possible PCI linear aperture support.

`clgd54xxclock` brute-forces Cirrus PLL numerator/denominator/post-divisor values against `RefFreq`. `init` validates the requested pixel clock against chip-family limits, programs VCLK3, sets depth-dependent pixel format and DAC mode, computes overflow bits, handles interlace, and marks high-memory graphics mode state.

`load` writes the computed sequencer, hidden DAC, CRT, and graphics registers. `clgd542xhwgc` is a registered but empty hardware-cursor placeholder.
