# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.c

Small unnormalized real FFT implementation used by Vorbis analysis.

Important routines:
- `drfti1()` and `fdrffti()` factor transform size and build trigonometric/split caches.
- Forward radix helpers: `dradf2()`, `dradf4()`, and `dradfg()`.
- `drftf1()` performs forward real FFT dispatch over factor stages.
- Backward radix helpers: `dradb2()`, `dradb3()`, `dradb4()`, and `dradbg()`.
- `drftb1()` performs backward real FFT dispatch.
- Public API:
  - `drft_forward()`
  - `drft_backward()`
  - `drft_init()`
  - `drft_clear()`

Behavior:
- Derived from OggSquish/NetLib-style FFT code, cut down for Vorbis.
- Supports factorized sizes and uses mixed radix routines.
- Transform packing is documented as FORTRAN-style real FFT packing.

Integration points:
- Declared by `smallft.h`.
- Used by psychoacoustic/envelope analysis and tuning tools.
- Allocates lookup caches using `_ogg_calloc()`.

Risk and review signals:
- Index-heavy numerical code; off-by-one changes are high risk.
- `drft_init()` does not check allocation failure.
- The implementation is unnormalized; callers must handle scaling.
- Input sizes are assumed to be codec-controlled block sizes.

Filesystem relevance:
- No filesystem logic. This is audio transform math.
