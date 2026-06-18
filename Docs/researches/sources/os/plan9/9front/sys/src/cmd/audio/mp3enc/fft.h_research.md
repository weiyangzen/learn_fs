# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.h

This header declares FFT analysis functions for the encoder.

Exports:
- `fft_long()`
- `fft_short()`
- `init_fft()`

Dependencies:
- Includes `encoder.h` for `BLKSIZE`, `BLKSIZE_s`, `sample_t`, `FLOAT`, and LAME structures.

Integration:
- Used by psychoacoustic model code to transform time-domain samples into frequency-domain energy data.
- `init_fft()` must be called during encoder initialization before analysis windows are used.

Risks:
- Function prototypes depend on fixed compile-time block sizes.
