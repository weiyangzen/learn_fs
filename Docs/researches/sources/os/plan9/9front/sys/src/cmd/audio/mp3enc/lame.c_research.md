# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.c

This file implements the central LAME encoder initialization, public encode-buffer API, flush/finalization, tag rewrite hook, and bitrate/statistics accessors.

Key responsibilities:
- Computes derived encoder parameters from user-facing `lame_global_flags`.
- Selects bitrate, samplerate, MPEG version, frame size, compression ratio, channel mode, and filters.
- Initializes internal feature flags, CPU feature flags, bitstream state, scalefactor bands, side-info length, ATH/nspsytune behavior, and VBR limits.
- Provides public encode APIs for sample_t, short, float, long, and interleaved short input.
- Handles buffering, resampling, optional stereo-to-mono mixing, frame feeding, and output byte accumulation.
- Flushes encoder delay/padding, writes trailing ID3v1 tags, and closes/free internal state.
- Rewrites Xing VBR tag into a seekable file after encoding.
- Provides bitrate and stereo-mode histograms.

Important initialization functions:
- `lame_init_params_ppflt_lowpass()`: computes polyphase lowpass band amplitudes.
- `lame_init_params_ppflt()`: computes lowpass/highpass transition bands and amplitudes.
- `optimum_bandwidth()`: estimates default lowpass/highpass based on bitrate, samplerate, and channel mode.
- `optimum_samplefreq()`: suggests output samplerate from lowpass/input constraints.
- `lame_init_qval()`: maps quality level to psy model, quantization, noise shaping, and Huffman-search flags.
- `lame_init_params()`: full derived-parameter initialization.
- `lame_init()` and `lame_init_old()`: allocate and default global/internal flags.

Important encode/finalize functions:
- `lame_print_config()`: reports version, CPU features, resampling, filters, and free-format warnings.
- `lame_encode_frame()`: dispatches to MP3 or optional Ogg frame encoder.
- `lame_encode_buffer_sample_t()`: main buffered encode path with resampling/fill-buffer integration.
- `lame_encode_buffer()`, `lame_encode_buffer_float()`, `lame_encode_buffer_long()`: type-converting wrappers.
- `lame_encode_buffer_interleaved()`: deinterleaves stereo short samples and encodes.
- `lame_encode()`: legacy 2x1152-frame API.
- `lame_encode_flush()`: feeds zero padding until internal samples are encoded, then flushes bitstream and writes ID3v1.
- `lame_close()`: frees internal state and possibly the `lame_global_flags`.
- `lame_encode_finish()`: flushes then closes.
- `lame_mp3_tags_fid()`: rewrites final Xing VBR tag through `PutVbrTag()`.

Statistics functions:
- `lame_bitrate_hist()`
- `lame_bitrate_kbps()`
- `lame_stereo_mode_hist()`
- `lame_bitrate_stereo_mode_hist()`

Dependencies and integration:
- Includes `lame-analysis.h`, `lame.h`, `util.h`, `bitstream.h`, `version.h`, `tables.h`, `quantize_pvt.h`, and `VbrTag.h`.
- Calls CPU feature probes, `init_bit_stream_w()`, `id3tag_write_v2()`, `InitVbrTag()`, `fill_buffer()`, `lame_encode_mp3_frame()`, `flush_bitstream()`, `id3tag_write_v1()`, `copy_buffer()`, `freegfc()`, and VBR tag rewriting.
- Optional Ogg/Vorbis and architecture-specific code is gated by preprocessor flags.

Initialization control flow:
- Establishes internal pointer and report callbacks.
- Detects CPU features and allocates ATH state.
- Determines input/output channel counts and disables MS for mono.
- Resolves bitrate/compression ratio/output samplerate.
- Sets MP3 frame size from MPEG version granule count.
- Estimates VBR compression ratio or CBR compression ratio.
- Chooses default stereo mode if not set.
- Computes default/user-driven lowpass and highpass filters.
- Maps samplerate/bitrate to MPEG table indexes.
- Disables VBR tags for CBR, Ogg, analysis, or pinfo modes.
- Initializes bitstream, scalefactor bands, side-info length, ID3v2, optional initial VBR header, MPEG flags, frame estimate, nspsytune, VBR/ATH behavior, and qval flags.

Encoding data flow:
- `lame_encode_buffer_sample_t()` fills internal `mfbuf` from caller input via `fill_buffer()`.
- Once enough samples are buffered for FFT and MDCT/filterbank requirements, it calls `lame_encode_frame()`.
- After a frame is encoded, it shifts old samples out of `mfbuf` by `gfp->framesize`.
- Wrapper APIs allocate temporary `sample_t` buffers and delegate to the sample_t path.

Risks and edge cases:
- Several allocation failure paths in buffer wrappers return `-2` without freeing the other buffer if only one allocation succeeded.
- `init_bit_stream_w()` allocation failure is not handled here.
- API is stateful and guarded by `gfc->Class_ID`; misuse before `lame_init_params()` returns `-3`.
- Many settings are silently adjusted, such as VBR disabled at high fixed bitrate, quality clamping, mode defaults, and samplerate decisions.
- `lame_encode_flush()` mutates `mf_samples_to_encode` while also calling encode paths that mutate it.
- VBR tag rewriting requires a seekable `FILE *`.
