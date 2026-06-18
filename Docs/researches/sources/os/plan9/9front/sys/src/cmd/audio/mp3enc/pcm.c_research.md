# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.c

## Scope
Experimental generalized PCM input, demultiplexing, scalar, and resampling implementation, compiled only under `KLEMM_44`.

## APIs and Behavior
When enabled, provides `octetstream_open/resize/close`, a generic `lame_encode_pcm()` path, `lame_encode_pcm_flush()`, compatibility wrappers for `lame_encode_buffer`, `lame_encode_buffer_interleaved`, and `lame_encode_flush`, scalar dot-product implementations, scalar dispatch selection by CPU features, `unround_samplefrequency()`, `resample_open()`, `resample_close()`, and `resample_buffer()`.

## Data and Algorithms
Contains u-law and A-law conversion tables, endian-aware demux functions for 8/16/24/32-bit integer PCM and 32/64/80-bit float PCM, demux metadata indexed by PCM type bitfields, channel conversion by averaging or duplication, optional resampling through FIR tables, amplification/fade handling, frame buffering, and encoder dispatch to Layer I/II/III, MPEG-plus, AAC, or Ogg paths when compiled.

## Dependencies
Includes `bitstream.h` and `id3tag.h` outside the compile gate, and under `KLEMM_44` includes `pcm.h` plus math/stdio/memory/system headers. Uses many internal fields from `lame_t`.

## Risks and Notes
Most code is inactive unless `KLEMM_44` is defined. Active code has debug tracing and writes `pcm_data.txt` in `lame_encode_frame()`. Several allocation results are unchecked, some error paths leak allocated buffers, and the implementation depends on internal `lame_t` layout not visible in this file.
