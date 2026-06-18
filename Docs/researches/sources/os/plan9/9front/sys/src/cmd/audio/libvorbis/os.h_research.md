# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/os.h

Platform abstraction header for libvorbis math, inline, allocation, and float-to-int helpers.

Important contents:
- Includes optional `config.h`, `<math.h>`, `<ogg/os_types.h>`, and `misc.h`.
- Defines `STIN`, fallback `M_PI`, `FAST_HYPOT`, `min`, and `max`.
- Provides fallback `rint()` definitions for platforms lacking it.
- Handles `alloca`/memory header portability.
- Defines optimized `vorbis_ftoi()` and FPU control helpers for i386 GCC, 32-bit MSVC, and SSE2-capable x86_64.
- Provides a portable fallback `vorbis_ftoi()` using `floor(f+.5)`.

Integration points:
- Included by many libvorbis implementation files: psychoacoustics, scales, FFT, synthesis, codebooks, residue, etc.
- The FPU helpers affect quantization and integer rounding behavior in codec paths.

Risk and review signals:
- Cross-platform code includes Windows, Symbian, DJGPP, GCC inline asm, and SSE2 intrinsics; some paths are irrelevant to Plan 9 builds but retained in vendored code.
- `min`/`max` macros evaluate arguments multiple times.
- FPU rounding behavior can affect bit-exact encoding decisions.

Filesystem relevance:
- No filesystem logic. This is codec portability glue.
