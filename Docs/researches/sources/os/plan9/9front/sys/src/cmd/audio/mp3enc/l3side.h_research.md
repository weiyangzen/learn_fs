# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/l3side.h

This header defines MPEG Layer III side-information and scalefactor data structures.

Key typedefs:
- `D576`, `I576`: 576-sample coefficient arrays.
- `D192_3`, `I192_3`: short-block grouped arrays.
- `scalefac_struct`: long and short scalefactor band boundaries.
- `III_psy_xmin`: long/short psychoacoustic threshold or energy arrays.
- `III_psy_ratio`: threshold and energy pair.
- `gr_info`: per-granule/channel side-info fields.
- `III_side_info_t`: frame-level Layer III side info.
- `III_scalefac_t`: encoded long/short scalefactors.

Dependencies and integration:
- Includes `encoder.h` and `machine.h`.
- Used by psychoacoustic, quantization, and bitstream code.
- `bitstream.c` serializes `III_side_info_t` and `III_scalefac_t`.
- `encoder.c` mutates block type, window flags, and stereo mode decisions.

Notable fields:
- `gr_info` contains MPEG fields such as `part2_3_length`, `big_values`, `global_gain`, `scalefac_compress`, `block_type`, region counts, Huffman table selectors, and LSF partition data.
- `III_side_info_t` includes reservoir fields `main_data_begin`, `resvDrain_pre`, and `resvDrain_post`.

Risks:
- Structures are tightly coupled to MPEG Layer III bitstream layout.
- Integer dimensions assume maximum two granules and two channels.
