# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.h

Central LAME internal utility header defining common constants, bitstream state, psychoacoustic state, VBR seek tracking, resampler state, and the large private encoder state structure.

Key contents:
- Defines fallback math constants, boolean constants, buffer sizing, min/max macros, and bitstream constants.
- Defines `Bit_stream_struc`, `nsPsy_t`, `VBR_seek_info_t`, `ATH_t`, `coding_t`, and `resample_t`.
- Defines `lame_internal_flags`, the main internal encoder context used across bitstream, quantization, psychoacoustic, MDCT, reservoir, ID3, VBR, ATH, CPU feature, and analyzer code.
- Declares utility functions implemented in `util.c`: cleanup, bitrate/sample-rate mapping, ATH/frequency helpers, frame-bit calculation, sample buffer filling, CPU probes, stats, message printing, and quickselect.

Dependencies:
- Includes `machine.h`, `encoder.h`, `lame.h`, `lame-analysis.h`, `id3tag.h`, and `l3side.h`.

Research notes:
- The header exposes many implementation details globally rather than hiding them behind an opaque type.
- `lame_internal_flags` carries both persistent encoder configuration and per-frame scratch/history state.
- Several fields and comments show this is an older vendored LAME codebase with optional compile-time variants.
