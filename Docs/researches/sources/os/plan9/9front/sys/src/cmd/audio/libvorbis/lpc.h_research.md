# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.h

Declaration header for low-level LPC helpers.

Important contents:
- Declares `vorbis_lpc_from_data()` for LPC coefficient estimation.
- Declares `vorbis_lpc_predict()` for sample prediction from coefficients.
- Includes `vorbis/codec.h`.

Integration points:
- Used by `lpc.c`, `floor0.c`, and `mapping0.c`.

Risk and review signals:
- Header only; callers must satisfy buffer and length requirements expected by `lpc.c`.

Filesystem relevance:
- No filesystem logic.
