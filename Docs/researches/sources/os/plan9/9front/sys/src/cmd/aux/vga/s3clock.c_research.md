# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3clock.c

S3-specific clock loading helper controller for programmable clocks that require S3 CRTC/Misc register sequencing.

Key behavior:
- `setcrt42` safely changes S3 CRTC register `0x42` clock-select bits by temporarily manipulating VGA Misc and sequencer state.
- `icd2061aload` serializes a 24-bit ICD2061A clock word using CRTC register `0x42` data/clock bits, including unlock, start, modified Manchester data, stop, and final clock selection. It repeats loading three times from the generic `load` dispatcher.
- `ch9294load` selects a Chrontel 9294-style clock through CRTC `0x42`.
- `tvp3025load` and `tvp3026load` program TI TVP3025/3026 RAMDAC clock registers through DAC-specific helpers, with special paths for 1-bpp standard clocks and 8-bpp programmed clocks.
- `init` validates that `vga->clock->name` matches a known clock prefix, initializes the underlying clock controller if necessary, supplies default pixel clock from the mode, and adjusts `vga->misc` for nonstandard clocks.
- `load` dispatches to the matching clock loader and marks the controller loaded.

Notable dependencies:
- External DAC helpers `tvp3020xo`, `tvp3026xo`, `tvp3026xi`.
- Existing `vga->clock` controller fields for M/N/P/D/I/Q clock parameters.
- Direct VGA port I/O.

Research notes:
- Busy waits for TVP3026 PLL lock are unbounded.
- Clock name matching strips a suffix after `-`, allowing speed-grade or variant suffixes.
- The controller is only meaningful when paired with a concrete clock/RAMDAC controller that has already computed PLL fields.
