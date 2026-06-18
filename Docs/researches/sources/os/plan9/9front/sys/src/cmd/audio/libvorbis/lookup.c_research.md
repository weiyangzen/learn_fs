# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.c

Lookup-table helper implementation for cosine, inverse-square-root, exponent scaling, and dB-to-linear conversions.

Important routines:
- Under `FLOAT_LOOKUP`:
  - `vorbis_coslook()` interpolates cosine over `[0, PI]`.
  - `vorbis_invsqlook()` interpolates `1/sqrt(p)` for `.5 <= p < 1`.
  - `vorbis_invsq2explook()` returns exponent correction values.
  - `vorbis_fromdBlook()` converts dB values in roughly `[-140, 0]` to linear multipliers.
- Under `INT_LOOKUP`:
  - `vorbis_invsqlook_i()` performs fixed/integer-style inverse-square-root scaling.
  - `vorbis_fromdBlook_i()` converts fixed-format dB to linear float.
  - `vorbis_coslook_i()` returns fixed-format cosine.

Integration points:
- Uses generated tables from `lookup_data.h`.
- `lsp.c` can include `lookup.c` directly when optimized lookup modes are enabled, though this local build undefines those modes in `lsp.c`.

Risk and review signals:
- Functions assume inputs are in documented domains; out-of-domain indexes can overrun lookup arrays.
- Conditional compilation means active symbols depend on `FLOAT_LOOKUP`/`INT_LOOKUP`.
- `vorbis_fromdBlook()` clamps outside-table values to `1.f` or `0.f`.

Filesystem relevance:
- No filesystem logic. This is numeric support for codec math.
