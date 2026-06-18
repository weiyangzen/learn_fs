# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevstc3.c

Purpose: Simple RGB pass-through/merge algorithm for `stcolor`, exposed as `gsrgb`.

Key behavior:
- For each pixel, consumes three byte components and emits one output byte containing `RED`, `GREEN`, and `BLUE` bits.
- On initialization, validates no white-line callbacks, byte data, exactly three color components, and non-direct input.

Important dependencies:
- `gdevstc.h`.

Notable risks / findings:
- No actual error diffusion; Ghostscript is expected to provide already-thresholded component bytes.
