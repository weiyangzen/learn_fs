# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.c

PCM envelope analysis implementation used by the Vorbis encoder to detect pre-echo/post-echo regions and guide block switching.

Important routines:
- `_ve_envelope_init()` initializes a 128-sample MDCT, sine-squared MDCT window, seven fixed envelope bands, per-channel filter state, and mark storage.
- `_ve_envelope_clear()` releases MDCT, band windows, filter state, and mark storage.
- `_ve_amp()` transforms a small PCM window, derives smoothed band amplitudes, tracks near-DC energy, compares recent max/min deltas against psychoacoustic pre/postecho thresholds, and returns trigger flags.
- `_ve_envelope_search()` scans buffered PCM in `searchstep` increments, grows mark storage as needed, updates pre/postecho marks, tracks stretch penalty, and reports whether enough unmarked/marked data exists for block decision.
- `_ve_envelope_mark()` checks whether the current Vorbis block overlaps an envelope trigger.
- `_ve_envelope_shift()` shifts mark/cursor state when PCM history is consumed.

Behavior:
- Uses seven hard-coded analysis bands and short MDCT windows rather than full psychoacoustic masking.
- Maintains a moving near-DC accumulator to avoid low-frequency leakage driving false triggers.
- Marks windows around both rising and falling amplitude deltas, with stretch logic to reduce repeated impulse sensitivity.

Integration points:
- Uses thresholds from `codec_setup_info.psy_g_param`.
- Uses `mdct.c`, `scales.h`, and `envelope.h`.
- Called from encoder block selection paths via `private_state->ve`.

Risk and review signals:
- `_ve_amp()` uses plain `malloc()` per analyzed channel/window and does not check allocation failure.
- Mark storage is dynamically reallocated to match PCM progress; malformed state or incorrect shift values could corrupt envelope timing.
- Trigger behavior is tuning-sensitive and should be regression-tested with impulses, fades, silence, and low-energy noise.

Filesystem relevance:
- No filesystem logic. It is audio encoder analysis code in the 9front libvorbis vendor subtree.
