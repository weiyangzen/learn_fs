# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/window.c

## Purpose

This file computes floating-point apodization windows for LPC analysis in the FLAC encoder. It is compiled only when `FLAC__INTEGER_ONLY_LIBRARY` is not defined. `stream_encoder.c` allocates and fills these windows during buffer resize, then applies them before LPC autocorrelation.

## Window Functions

The file implements these window generators:

- `FLAC__window_bartlett()`: triangular Bartlett window with separate odd/even handling.
- `FLAC__window_bartlett_hann()`: Bartlett-Hann blend using absolute center distance and cosine taper.
- `FLAC__window_blackman()`: standard Blackman coefficients.
- `FLAC__window_blackman_harris_4term_92db_sidelobe()`: 4-term Blackman-Harris window.
- `FLAC__window_connes()`: squared parabolic Connes window.
- `FLAC__window_flattop()`: flat-top cosine-series window.
- `FLAC__window_gauss()`: Gaussian window with validated standard deviation; invalid or NaN values recurse to a default.
- `FLAC__window_hamming()`: Hamming window.
- `FLAC__window_hann()`: Hann window.
- `FLAC__window_kaiser_bessel()`: Kaiser-Bessel-derived cosine approximation.
- `FLAC__window_nuttall()`: Nuttall cosine-series window.
- `FLAC__window_rectangle()`: all ones.
- `FLAC__window_triangle()`: triangular window using `L + 1` denominator.
- `FLAC__window_tukey()`: rectangle/Hann hybrids with parameter validation and NaN fallback.
- `FLAC__window_partial_tukey()`: zero outside a selected `[start, end)` region, Tukey-tapered inside.
- `FLAC__window_punchout_tukey()`: inverse-style Tukey with a zeroed middle region and tapered kept regions.
- `FLAC__window_welch()`: parabolic Welch window.

## Parameter Handling

Several parameterized windows guard invalid values:

- Gaussian `stddev` must be `0 < stddev <= 0.5`; invalid values fall back to `0.25`.
- Tukey `p <= 0` becomes rectangular; `p >= 1` becomes Hann; NaN-like invalid values fall back to `0.5`.
- Partial and punchout Tukey clamp invalid `p` by recursively using `0.05`, `0.95`, or `0.5`.

Most functions assume a positive length `L` supplied by the encoder. They compute `N = L - 1` where needed and fill exactly `L` entries.

## Key Dependencies

- `<math.h>` for `cosf`, `fabsf`, `exp`, and `M_PI`.
- `FLAC/format.h` and `private/window.h` for FLAC types and declarations.
- `share/compat.h` for portability.
- MSVC warning pragmas suppress float conversion warnings around the implementation.

## Relationship to Encoder

`stream_encoder.c` parses apodization names such as `tukey(5e-1)`, `subdivide_tukey(2)`, `partial_tukey(...)`, and `punchout_tukey(...)`. During buffer allocation or blocksize changes, it calls these functions to precompute windows. LPC analysis then multiplies integer samples by the selected window before autocorrelation and coefficient search.

## Research Notes

This file is mathematically simple and self-contained. Its correctness depends on matching libFLAC's expected window formulas and edge behavior. Parameter validation is intentionally local so malformed apodization specifications do not propagate NaN-heavy windows into LPC analysis.
