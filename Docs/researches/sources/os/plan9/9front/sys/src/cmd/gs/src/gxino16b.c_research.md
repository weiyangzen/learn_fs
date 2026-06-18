# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxino16b.c

Dummy build-time stub for unsupported 16-bit image sample unpacking.

Key behavior:
- Includes the sample unpacking type definition.
- Defines `sample_unpack_16_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The common image setup code consults this pointer for 16-bit samples; this stub disables 16-bit unpacking in builds that include it.
