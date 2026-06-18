# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/trio64.c

S3 Trio64 controller support and shared Trio/ViRGE PLL calculation helper.

Key behavior:
- Snarfs extra sequencer registers `Seq08-Seq18` plus CRTC ID registers, then delegates to `s3generic`.
- Advertises linear, 2x8 pixel clock, and enhanced mode.
- `trio64clock()` computes PLL `M/N/R` for S3 internal clock generators under part-specific limits stored in `vga->m/n/r/f[1]`.
- Rejects depths above 8 bpp.
- Uses fixed VGA clocks when possible, otherwise programs `Seq12/Seq13` PLL fields and misc clock-select bits.
- Enables internal clock generator and optional 2x8 mode.
- Configures FIFO start, memory access, VLB latch delay, and advanced function control.

Integration:
- Exports `Ctlr trio64` and function `trio64clock()` reused by `virge.c`.

Filesystem relevance:
- Indirect display hardware support.
