# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/timer.h

This header declares libmad's rational timer type and timer utility API.

Key declarations:
- `mad_timer_t`: signed whole seconds plus an unsigned fractional part.
- `mad_timer_zero`: external zero constant.
- `MAD_TIMER_RESOLUTION`: `352800000UL`, chosen to be divisible by common audio/video timing rates.
- `enum mad_units`: units for hours, minutes, seconds, metric fractions, audio sample rates, video frame rates, CD frames, and drop-frame-like rates.
- Timer operations for reset, compare, sign, negate, absolute value, set, add, multiply, count, fraction extraction, and formatting.

Dependencies and integration:
- This is a public libmad utility header. Implementations are outside this file.
- Audio rates listed include 8 kHz through 48 kHz, matching MPEG samplerates and common PCM rates.
- The API can represent playback durations, sample counts, and time strings for decoder applications.

Risks and edge cases:
- Negative enum values are used for aggregate units and drop-frame variants, so callers must pass valid enum values to the implementation.
- The fractional resolution is large but still integer-based; overflow behavior depends on implementation code not present here.
