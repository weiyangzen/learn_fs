# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.c

This file manages the MP3 Layer III bit reservoir. It calculates frame capacity, distributes reservoir bits to granules, tracks surplus/deficit after quantization, and schedules stuffing/drain bits.

Key responsibilities:
- Computes the maximum reservoir size allowed for the current MPEG version, frame length, strict ISO mode, and `disable_reservoir`.
- Reports available frame bits at the beginning of a frame through `ResvFrameBegin()`.
- Computes target and extra bits for a granule through `ResvMaxBits()`.
- Updates reservoir size after each granule with `ResvAdjust()`.
- Byte-aligns and drains surplus bits at frame end with `ResvFrameEnd()`.

Important functions:
- `ResvFrameBegin(lame_global_flags *gfp, III_side_info_t *l3_side, int mean_bits, int frameLength)`: sets `gfc->ResvMax`, clears pre-drain, updates pinfo, and returns full frame bit capacity.
- `ResvMaxBits(...)`: returns base `targ_bits` and allowed `extra_bits` from the reservoir.
- `ResvAdjust(...)`: adds unused bits or subtracts overuse after quantization.
- `ResvFrameEnd(...)`: drains stuffing bits to keep reservoir byte-aligned and within max.

Control/data flow:
- `quantize.c` calls `ResvFrameBegin()` before allocation, `ResvMaxBits()` for CBR PE-based targets, `ResvAdjust()` after each final granule/channel, and `ResvFrameEnd()` after the frame.
- Bitstream formatting later uses `l3_side->resvDrain_pre`, `resvDrain_post`, and `main_data_begin`.

Notable behavior:
- MPEG-1 reservoir limit is `8*511`; MPEG-2 uses `8*255`.
- Strict ISO max frame buffer is `8*960`; non-strict allows `8*2047`.
- If the reservoir is almost full, target bits are increased to burn surplus; otherwise, CBR can reserve about 10 percent of mean bits to build reservoir.
- The active code drains all stuffing into current-frame ancillary data. The alternate `NEW_DRAIN` path is disabled because the file defines `NEW_DRAINXX`, not `NEW_DRAIN`.

Risks and edge cases:
- Reservoir accounting is integer/bit exact; any mismatch with bitstream formatter can corrupt `main_data_begin`.
- `ResvAdjust()` does not use its `l3_side` argument.
- The disabled `NEW_DRAIN` path suggests historical uncertainty around pre/post drain behavior.
- Assertions require byte-aligned `ResvMax` and overage values.
