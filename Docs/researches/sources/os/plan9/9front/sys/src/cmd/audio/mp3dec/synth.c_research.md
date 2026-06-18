# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.c

This file is libmad's MPEG audio synthesis stage. It converts decoded subband samples from `struct mad_frame` into fixed-point PCM samples stored in `struct mad_synth.pcm`.

Key responsibilities:
- Initializes and resets synthesis state with `mad_synth_init()` and `mad_synth_mute()`.
- Implements a fixed-point 32-point DCT in `dct32()`.
- Maintains a 16-phase polyphase synthesis filter history in `synth->filter`.
- Applies the synthesis window coefficients from included `D.dat`.
- Emits either full-rate 32 samples per subband sample or half-rate 16 samples when `MAD_OPTION_HALFSAMPLERATE` is set.
- Updates `pcm.samplerate`, `pcm.channels`, `pcm.length`, and the rolling `phase`.

Important functions:
- `mad_synth_init(struct mad_synth *synth)`: clears filter history, sets phase to zero, and clears PCM metadata.
- `mad_synth_mute(struct mad_synth *synth)`: zeros all per-channel filterbank history entries.
- `dct32(...)`: static, optimized DCT used by both synthesis paths.
- `synth_full(...)`: full-frequency PCM synthesis.
- `synth_half(...)`: half-frequency PCM synthesis that emits only every other output sample position.
- `mad_synth_frame(...)`: public entry point for one decoded frame.

Dependencies and integration:
- Includes `global.h`, `fixed.h`, `frame.h`, and `synth.h`.
- Depends on libmad fixed-point arithmetic helpers/macros such as `mad_f_mul`, `MAD_F_ML0`, `MAD_F_MLA`, `MAD_F_MLZ`, and `MAD_F()`.
- Uses `MAD_NCHANNELS()` and `MAD_NSBSAMPLES()` from frame/header logic.
- The `D` coefficient table is compiled by including `D.dat` into a static `D[17][32]`.

Control flow:
- `mad_synth_frame()` derives channel count and subband sample count from the frame header.
- It sets PCM output metadata, chooses `synth_full` or `synth_half`, invokes the selected synthesis routine, then advances phase by the number of subband samples modulo 16.
- Each synthesis routine loops channels, then subband sample slots, performs `dct32()`, and applies synthesis-window multiply-accumulate patterns into PCM output.

Notable implementation details:
- Optional `OPT_SSO` shifts reduce fixed-point multiply cost at some accuracy cost.
- `FPM_DEFAULT` enables `OPT_SSO` automatically because the comment says avoiding SSO loses both performance and accuracy for that mode.
- `OPT_DCTO` can use `MAD_F_MLX` for a DCT speed path when available.
- The DCT is manually unrolled and uses many temporaries for speed.
- Half-rate synthesis still runs the DCT and filterbank update but writes a reduced PCM sequence.

Risks and edge cases:
- The code assumes fixed array dimensions from `struct mad_synth` and `struct mad_frame`; malformed upstream frame metadata would be dangerous if invariants are broken.
- Many arithmetic paths rely on compile-time fixed-point macro consistency; `OPT_SSO` explicitly requires `MAD_F_FRACBITS == 28`.
- The synthesis loops are performance-sensitive and hard to audit because the filterbank arithmetic is heavily unrolled.
- No direct filesystem behavior is present.
