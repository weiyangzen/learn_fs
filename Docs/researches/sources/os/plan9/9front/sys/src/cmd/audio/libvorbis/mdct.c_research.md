# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.c

Normalized modified discrete cosine transform implementation for Vorbis power-of-two block sizes.

Important routines:
- `mdct_init()` allocates trigonometric and bit-reversal lookup tables, computes log2 block size, and stores scaling.
- `mdct_clear()` releases lookup allocations.
- Internal butterfly routines implement 8-, 16-, 32-, first-stage, and generic-stage MDCT butterflies.
- `mdct_bitreverse()` performs bit-reversal and final pre/post rotations.
- `mdct_backward()` runs inverse MDCT from spectral input to time-domain output.
- `mdct_forward()` runs forward MDCT from time-domain input to spectral output, using temporary work storage.

Implementation notes:
- Supports optional integerized transform through macros in `mdct.h`, but default is float.
- The module intentionally excludes window generation/application; callers handle windowing.
- Forward transform allocates a full-size temporary work buffer per call.

Integration points:
- Used by `envelope.c` for short envelope MDCT.
- Used by `mapping0.c` for encode/decode transform.
- Lookup objects are stored in `private_state->transform` and `envelope_lookup.mdct`.

Risk and review signals:
- `mdct_init()` and `mdct_forward()` use allocation without checking failure.
- Assumes power-of-two length at least 64 as validated by Vorbis header/setup paths.
- Transform correctness is sensitive to lookup generation, bit reversal, and block size.

Filesystem relevance:
- No filesystem logic. It is audio transform math.
