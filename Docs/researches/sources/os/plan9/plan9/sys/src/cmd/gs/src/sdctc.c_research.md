# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdctc.c

Small common implementation file for DCT encode/decode streams.

It defines the public GC descriptor for `stream_DCT_state` and implements `s_DCT_set_defaults`.

Defaults set:

- `jpeg_memory` to Ghostscript’s non-GC library memory.
- `data.common` to null.
- `ColorTransform` to `-1` meaning unspecified.
- `QFactor` to `1.0`.
- `Markers` to an empty string.

This is shared DCT/JPEG filter initialization support, not filesystem code.
