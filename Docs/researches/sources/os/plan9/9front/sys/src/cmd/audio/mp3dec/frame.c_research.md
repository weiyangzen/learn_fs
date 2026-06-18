# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.c

This file decodes MPEG audio frame headers, chooses the layer decoder, and manages frame-level state. It defines bitrate and sample-rate lookup tables, maps layers I/II/III to `mad_layer_I`, `mad_layer_II`, and `mad_layer_III`, and implements initialization/cleanup for `mad_header` and `mad_frame`.

`decode_header` parses sync, MPEG version flags including unofficial MPEG 2.5, layer, CRC protection, bitrate index, sample rate, padding, private bit, mode, mode extension, copyright/original flags, and emphasis. `mad_header_decode` handles stream sync, skip requests, free-format bitrate detection, next-frame length calculation, buffer-length validation, and incomplete-header marking. `free_bitrate` scans for the next compatible frame to infer free-format rate.

`mad_frame_decode` ensures a header exists, dispatches to the appropriate layer decoder, and records ancillary data boundaries for non-Layer III frames. `mad_frame_mute` zeroes all subband samples and any Layer III overlap buffer. This file is the bridge between byte stream management and actual MPEG layer decoding.
