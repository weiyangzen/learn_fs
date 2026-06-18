# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/mpglib_interface.c

## Scope
Conditional wrapper exposing LAME decode APIs over mpglib/mpg123 internals.

## APIs and Behavior
Compiled only under `HAVE_MPGLIB`. Maintains global `MPSTR mp` decoder state. `lame_decode_init()` calls `InitMP3`. `lame_decode1_headers()` decodes at most one frame, fills `mp3data_struct` from parsed headers, computes bitrate from frame size or bitrate table, handles Xing frame count, and deinterleaves mpglib output into left/right PCM arrays. `lame_decode1`, `lame_decode_headers`, and `lame_decode` layer simpler interfaces over that core routine.

## Dependencies
Requires mpglib `interface.h`, `lame.h`, mpg123 tables/state such as `freqs` and `tabsel_123`.

## Risks and Notes
Uses static output buffer `char out[8192]` and global decoder state, so the interface is not reentrant. Several impossible states use `assert(0)`. Header fields are zeroed only partially; callers should not assume untouched fields are reset unless set by this path.
