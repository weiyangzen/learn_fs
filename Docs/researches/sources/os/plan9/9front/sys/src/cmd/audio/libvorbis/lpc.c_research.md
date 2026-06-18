# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.c

Low-level LPC routines for linear predictive coding support.

Important routines:
- `vorbis_lpc_from_data()` computes autocorrelation coefficients from time-domain data, runs Levinson-Durbin recursion to derive LPC coefficients, applies slight damping, writes float coefficients, and returns residual/error energy.
- `vorbis_lpc_predict()` predicts output samples from LPC coefficients and optional prime history.

Implementation notes:
- Autocorrelation and LPC coefficient accumulation use `double` for depth.
- The LPC error floor uses an epsilon based on signal energy.
- The code preserves separate Degener/Bormann copyright notice for derived autocorrelation/LPC logic.

Integration points:
- Declared in `lpc.h`.
- Included by floor and mapping code; floor0 uses LPC/LSP concepts for spectral envelope work.

Risk and review signals:
- Uses plain `malloc()` for temporary arrays and does not check allocation failure.
- `vorbis_lpc_predict()` allocates `m+n` samples for work storage.
- Input sizes/order must be sensible; no defensive validation is performed in these helpers.

Filesystem relevance:
- No filesystem logic. This is audio signal-processing math.
