# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdmarker.c

JPEG marker reader, marker parameter parser, restart resynchronizer, and APP/COM marker handling.

Key points:
- Defines JPEG marker codes and a permanent marker reader with overridable COM/APPn processors and optional marker-saving state.
- Byte-input macros preserve source restart points so marker parsing can suspend and reprocess safely.
- Parses SOI, SOF, SOS, DHT, DQT, DRI, optional DAC, APP0/JFIF, APP14/Adobe, COM, and unknown variable markers.
- SOI resets arithmetic tables, restart interval, colorspace assumptions, density defaults, and JFIF/Adobe flags.
- SOF validates image dimensions, component count, duplicate frame markers, component sampling, and quant-table selectors.
- SOS maps scan component IDs to SOF components, records entropy table selectors and spectral/progressive parameters, and increments scan count.
- DHT/DQT readers minimally validate lengths while converting quant tables from zigzag to natural order.
- APP0/APP14 are examined by default for JFIF/JFXX and Adobe transform metadata; other APP/COM markers are skipped unless saving or custom processors are installed.
- `next_marker` skips extraneous bytes and stuffed-zero sequences while warning about discarded data.
- `read_restart_marker` and `jpeg_resync_to_restart` implement stream-only restart recovery using discard, scan-forward, or leave-marker-unread strategies.
- `jpeg_save_markers` and `jpeg_set_marker_processor` expose application control over metadata retention and marker parsing.

Dependencies and interactions:
- Called by `jdinput.c` for header and inter-scan marker consumption.
- Entropy decoders call restart reading/resync methods at restart intervals.
- Source managers provide `fill_input_buffer`, `skip_input_data`, and optional custom restart resync.

Risk notes:
- Unsupported SOF types, reserved markers, arithmetic decoding in non-arithmetic builds, and malformed marker lengths are fatal.
- DNL is ignored, so files with initially unknown height are not supported.
- Saving very large APP/COM markers is bounded by the memory manager's max allocation chunk and can still consume image-pool memory.
