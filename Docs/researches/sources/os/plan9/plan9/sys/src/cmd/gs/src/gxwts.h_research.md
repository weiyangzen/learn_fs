# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.h

Defines Ghostscript well-tempered screening data structures. It introduces 16-bit screen samples, the base `wts_screen_t` shape, and three screen types: rational, J, and H screens.

Key structures:
- `wts_screen_s`: common screen type, cell dimensions, shift, and sample buffer.
- `wts_screen_j_t`: probability/jump-based screen variant with A/B horizontal and C/D vertical jumps.
- `wts_screen_h_t`: H-screen variant storing exact `px`/`py` targets and integer split positions.
- `wts_get_samples(...)`: exported accessor for sample runs at a given coordinate.

This is a small rendering/halftone support header; it has no filesystem or OS-facing behavior.
