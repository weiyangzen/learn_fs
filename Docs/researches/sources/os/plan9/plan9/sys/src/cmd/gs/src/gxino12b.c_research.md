# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino12b.c

Dummy build-time stub for unsupported 12-bit image sample unpacking.

Key behavior:
- Includes Ghostscript base/sample type headers.
- Defines `sample_unpack_12_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The shared image setup code consults this pointer for 12-bit samples; null makes unsupported 12-bit cases fail with `rangecheck`.
