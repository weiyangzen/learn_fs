# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/scales.h

Inline scale conversion helpers for Vorbis psychoacoustic and codec math.

Important contents:
- Defines `unitnorm()` using float bit manipulation when `VORBIS_IEEE_FLOAT32` is enabled.
- Defines `todB()` fast dB approximation using IEEE float exponent/mantissa bits.
- Defines fallback `unitnorm()`, `todB()`, and `todB_nn()` for non-IEEE builds.
- Defines `fromdB()`.
- Defines Bark, Mel, and octave conversion macros: `toBARK`, `fromBARK`, `toMEL`, `fromMEL`, `toOC`, and `fromOC`.

Integration points:
- Included by psychoacoustic, floor, LSP, codebook, and tuning utilities.
- Depends on `os.h` for platform details and Ogg integer types.

Risk and review signals:
- Fast `todB()` assumes IEEE 32-bit float layout.
- Macros evaluate arguments directly; avoid side-effect expressions.
- Scale approximations are part of codec tuning behavior and should not be “simplified” casually.

Filesystem relevance:
- No filesystem logic. It is audio/math helper code.
