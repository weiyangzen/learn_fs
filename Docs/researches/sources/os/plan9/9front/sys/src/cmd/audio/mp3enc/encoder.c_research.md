# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.c

This file orchestrates encoding of one MP3 frame.

Key responsibilities:
- Initializes per-frame encoder state on first use.
- Applies padding policy.
- Runs psychoacoustic analysis or fallback block defaults.
- Adjusts ATH for low-volume content.
- Runs MDCT/polyphase analysis and short-block reordering.
- Chooses LR vs MS stereo coding.
- Selects quantization loop according to CBR/VBR/ABR mode.
- Writes encoded frame data to the bitstream.
- Updates VBR frame accounting and analysis/statistics output.

Important functions:
- `adjust_ATH(lame_global_flags *gfp, FLOAT8 tot_ener[2][4])`: dynamically lowers/raises ATH adjustment based on frame energy and VBR mode.
- `lame_encode_mp3_frame(...)`: main one-frame encoding function.

Dependencies and integration:
- Includes `lame.h`, `util.h`, `newmdct.h`, `psymodel.h`, `quantize.h`, `quantize_pvt.h`, `bitstream.h`, and `VbrTag.h`.
- Calls psychoacoustic functions `L3psycho_anal()` or `L3psycho_anal_ns()`.
- Calls `mdct_sub48()` and `freorder()`.
- Calls quantization functions `iteration_loop()`, `VBR_quantize()`, `VBR_iteration_loop()`, or `ABR_iteration_loop()`.
- Calls `format_bitstream()` and `copy_buffer()` through bitstream code.
- Calls `AddVbrFrame()` when VBR tagging is enabled.

Control flow:
- On first frame, initializes padding state, primes MDCT/filterbank with zero-prefixed samples, calls `iteration_init()`, and configures ATH decay.
- For each frame, computes padding, obtains masking/energy data, sets block types and window-switch flags, runs MDCT, optionally computes MS stereo, writes analyzer data, quantizes, formats the bitstream, copies output, updates stats, and returns byte count.

Notable behavior:
- `force_ms` overrides automatic MS decisions.
- Automatic MS uses both MS energy ratios and perceptual entropy comparison.
- nspsytune mode applies a 19-tap FIR smoothing/normalization over perceptual entropy before quantization in CBR/ABR.
- The function uses stack arrays for MDCT coefficients, quantized coefficients, masking ratios, and scalefactors except on old Macintosh builds.

Risks and edge cases:
- Many invariants are asserted: buffer size, FFT offset, MDCT/filterbank sample availability, and bit accounting.
- The first-frame initialization mutates persistent `gfc` state and assumes valid `mf_size`.
- Some math paths use integer sums from floating-point perceptual entropy values.
- `mp3count` can be negative if downstream buffer copying fails.
