# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.c

LAME utility implementation for encoder housekeeping, psychoacoustic helpers, sample-rate/bitrate mapping, resampling, diagnostics, CPU feature probing, and simple statistics.

Key responsibilities:
- Frees `lame_internal_flags` owned buffers in `freegfc()`, including resampler/filter state, bitstream buffer, VBR seek table, and ATH data.
- Implements several ATH formulas and dispatches through `ATHformula()` based on `gfp->ATHtype`.
- Converts frequencies to Bark scale and critical-band width.
- Computes frame bit budgets in `getframebits()` and maps legal bitrate/sample-rate values through `FindNearestBitrate()`, `BitrateIndex()`, `SmpFrqIndex()`, and `map2MP3Frequency()`.
- Reorders short-block spectral coefficients in `freorder()`.
- Provides FIR Blackman-window resampling in `fill_buffer()` and `fill_buffer_resample()` when `KLEMM_44` is not enabled.
- Routes debug/message/error output through caller callbacks or `stderr`.
- Provides optional NASM-backed CPU feature probes and updates bitrate/stereo-mode histograms.
- Implements in-place quickselect-like `select_kth_int()` and platform-specific floating-point exception setup.

Dependencies:
- Uses LAME internal structures from `util.h`, MPEG tables such as `bitrate_table`, and math/libc routines.
- Resampling depends on persistent buffers in `lame_internal_flags`.

Research notes:
- `select_kth_int()` intentionally reorders its input array.
- Resampling lazily allocates filter tables and historical input buffers; `freegfc()` owns cleanup.
- CPU feature probes return false unless built with NASM support.
