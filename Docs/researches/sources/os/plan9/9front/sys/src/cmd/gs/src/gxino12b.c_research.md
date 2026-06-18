# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino12b.c

Dummy build-time stub for unsupported 12-bit image sample unpacking.

Key behavior:
- Includes the sample unpacking type definition.
- Defines `sample_unpack_12_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The shared image pipeline checks this pointer when 12-bit samples are requested; a null value makes unsupported cases fail with rangecheck.
