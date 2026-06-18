# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/window.h

## Role

`private/window.h` declares apodization window generation functions used by LPC analysis in non-integer-only FLAC encoder builds.

## API Surface

It declares Bartlett, Bartlett-Hann, Blackman, Blackman-Harris, Connes, flattop, Gauss, Hamming, Hann, Kaiser-Bessel, Nuttall, rectangle, triangle, Tukey, partial Tukey, punchout Tukey, and Welch window functions.

Each writes `window[0, L-1]` for a requested length `L`. Some take parameters such as Gaussian standard deviation or Tukey shape/start/end.

## Risks / Edge Cases

The entire API is disabled for `FLAC__INTEGER_ONLY_LIBRARY`. Parameter constraints such as `0.0 < stddev <= 0.5` for Gauss are documented here and must be enforced by callers or implementation.

## Dependencies

Includes `private/float.h` and `FLAC/format.h`.
