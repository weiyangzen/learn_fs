# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.h

Defines weighted threshold screen data structures for Ghostscript halftoning.

Key points:
- Defines `wts_screen_sample_t` as `bits16`, plus opaque `wts_screen_t`.
- Supports screen types `WTS_SCREEN_RAT`, `WTS_SCREEN_J`, and `WTS_SCREEN_H`.
- Base `wts_screen_s` stores cell dimensions, shift, type, and sample buffer.
- `wts_screen_j_t` adds jump probabilities and coordinate deltas for J-style screens.
- `wts_screen_h_t` adds exact split proportions and integer split positions for H-style screens.
- Declares `wts_get_samples`, which maps an `(x,y)` location to sample data and count.

Research notes:
- This is a compact internal interface; implementation is elsewhere.
- The fields are layout/algorithm parameters for screen sample lookup, not general graphics state.
