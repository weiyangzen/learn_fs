# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ark2000pv.c

`ark2000pv.c` is a VGA controller module for the ARK Logic ARK2000PV accelerator. It unlocks extended registers, snarfs sequencer/crt state and coprocessor status, and derives VRAM size from sequencer register bits.

It advertises linear aperture and `Hpclk2x8` support. Initialization handles optional pixel-clock doubling timing adjustments, CRT overflow bits, interlace registers, memory/aperture mode, depth-specific setup for 1 bpp and 8 bpp, FIFO/pitch control by horizontal size, clock select bits, and palette black entry.

`load` performs a careful clock switch, optionally toggles the sequencer for a W30C516 RAMDAC quirk, enables linear aperture if requested, writes aperture base/size registers, and writes extended sequencer/CRT registers. `dump` prints relevant extended state.

It exposes `ark2000pv` and placeholder `ark2000pvhwgc` controllers.
