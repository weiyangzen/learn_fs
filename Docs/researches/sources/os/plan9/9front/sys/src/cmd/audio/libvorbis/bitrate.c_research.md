# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/bitrate.c

## Role

This file implements libvorbis encode-side bitrate tracking and management. It selects among alternate packet blobs, manages bitrate reservoirs, enforces min/max constraints, and flushes the chosen packet.

## Initialization

`vorbis_bitrate_init(vorbis_info *vi, bitrate_manager_state *bm)` reads `bitrate_manager_info` from codec setup. When `reservoir_bits > 0`, it enables managed mode, computes per-half-block average/min/max target bit counts, initializes short/long block scaling, starts `avgfloat` at the middle packet blob, and initializes reservoirs to the configured bias fill.

`vorbis_bitrate_clear()` zeroes state.

`vorbis_bitrate_managed()` reports whether a block's DSP state is in managed mode.

## Block Submission

`vorbis_bitrate_addblock(vorbis_block *vb)` stores the submitted block. For unmanaged streams, it simply buffers one block for the common flush path.

For managed streams it:

1. Starts from the middle packet blob.
2. Uses the average reservoir to slew `avgfloat` toward higher or lower quality packet choices.
3. Enforces minimum bitrate by choosing larger packets or padding.
4. Enforces maximum bitrate by choosing smaller packets or truncating.
5. Updates min/max and average reservoirs after final packet size is known.

Packet blobs are stored in `vorbis_block_internal->packetblob[]`, with `PACKETBLOBS/2` being the normal packet.

## Packet Flush

`vorbis_bitrate_flushpacket(vorbis_dsp_state *vd, ogg_packet *op)` exposes the selected packet as an `ogg_packet`, using the managed choice when active or the middle blob otherwise, then clears the pending block pointer.

## Risks

The manager can truncate packets when max constraints cannot be met by choosing a smaller blob. Correctness depends on mapping code producing valid alternate packet blobs and on callers using the add/flush API for managed streams.
