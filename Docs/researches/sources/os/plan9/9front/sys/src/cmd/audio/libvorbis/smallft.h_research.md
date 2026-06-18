# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.h

Header for the small real FFT implementation.

Important contents:
- Defines `drft_lookup`, containing transform size, trig cache, and split/factor cache.
- Declares:
  - `drft_forward()`
  - `drft_backward()`
  - `drft_init()`
  - `drft_clear()`

Integration points:
- Included by `psy.h`, `psy.c`, `psytune.c`, and other analysis code.
- Depends on `vorbis/codec.h`.

Risk and review signals:
- Lookup owns heap buffers initialized by `drft_init()` and released by `drft_clear()`.
- No inline logic; behavior is in `smallft.c`.

Filesystem relevance:
- No filesystem logic. It is transform API declaration.
