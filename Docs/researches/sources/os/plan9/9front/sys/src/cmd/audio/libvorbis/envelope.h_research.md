# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.h

Header for Vorbis PCM envelope analysis state and operations.

Important contents:
- Defines analysis constants: `VE_PRE`, `VE_WIN`, `VE_POST`, `VE_AMP`, `VE_BANDS`, `VE_NEARDC`, and stretch bounds.
- Defines `envelope_filter_state`, holding per-band amplitude ring buffer and near-DC accumulator state.
- Defines `envelope_band`, holding band begin/end indexes, a weighting window, and normalization total.
- Defines `envelope_lookup`, the full runtime envelope analyzer state: channel count, window/search sizes, MDCT lookup/window, bands, per-channel filters, stretch, mark array, storage size, current offset, current mark, and cursor.
- Declares init, clear, search, shift, and mark functions implemented in `envelope.c`.

Integration points:
- Included by `codec_internal.h` and `envelope.c`.
- Depends on `mdct.h`.

Risk and review signals:
- The structs expose raw pointers and counters; callers must initialize with `_ve_envelope_init()` and clear with `_ve_envelope_clear()`.
- Mark/cursor values are sample-position state and must stay synchronized with PCM buffer shifting.

Filesystem relevance:
- No filesystem logic; this is codec analysis state.
