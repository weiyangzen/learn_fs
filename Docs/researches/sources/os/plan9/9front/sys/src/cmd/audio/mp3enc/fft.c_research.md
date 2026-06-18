# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.c

This file implements FFT/FHT routines used by the psychoacoustic model.

Key responsibilities:
- Provides an in-place Fast Hartley Transform implementation unless `USE_FFT3DN` redirects to `fht_3DN`.
- Performs windowed long and short transforms over encoder PCM buffers.
- Initializes long and short analysis windows.

Important functions:
- `fht(FLOAT *fz, int n)`: static Hartley transform using precomputed trig values.
- `fft_short(lame_internal_flags *gfc, FLOAT x_real[3][BLKSIZE_s], int chn, const sample_t *buffer[2])`: computes three short-window transforms.
- `fft_long(lame_internal_flags *gfc, FLOAT x[BLKSIZE], int chn, const sample_t *buffer[2])`: computes one long-window transform.
- `init_fft(lame_internal_flags *gfc)`: fills Blackman long window and Hann-style short window.

Dependencies and integration:
- Includes `util.h` and `fft.h`.
- Uses window arrays stored in `lame_internal_flags`.
- Called by psychoacoustic analysis code outside this group.

Notable implementation details:
- Uses a 256-entry bit-reversal table.
- Macro families (`ml*`, `ms*`) combine window lookup and PCM buffer access for speed.
- Long window uses Blackman coefficients.
- Short window stores only half-window coefficients.

Risks and edge cases:
- The file's header comments mention patent/licensing history around FHT/trig algorithms.
- Assumes buffer offsets supplied by caller are valid for 1024- and 256-point windows.
- Heavy macro arithmetic makes indexing correctness important and non-obvious.
