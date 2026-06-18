# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/analysis.c

## Role

This file implements single-block Vorbis analysis dispatch for encoding. It is part of the vendored libvorbis encoder.

## Main Interface

`vorbis_analysis(vorbis_block *vb, ogg_packet *op)` resets block bit counters and packet blobs, dispatches the block to mapping type 0 via `_mapping_P[0]->forward(vb)`, and optionally exposes the encoded packet through `ogg_packet`.

If bitrate management is active and the caller requests a packet directly, it returns `OV_EINVAL`; managed streams must use the bitrate manager interface.

## Packet Output

For unmanaged encoding, the output packet points at `vb->opb`'s buffer. It sets packet byte count, BOS/EOS flags, granule position, and sequence number.

## Analysis Debug Support

Under `ANALYSIS`, the file defines `_analysis_output_always()` and `_analysis_output()` to dump vectors to MATLAB-style `.m` files, optionally converting X-axis to Bark scale and values to dB.

## Dependencies

The file depends on libogg bit packing, Vorbis codec internals, mapping registry, scales, OS helpers, and misc helpers.
