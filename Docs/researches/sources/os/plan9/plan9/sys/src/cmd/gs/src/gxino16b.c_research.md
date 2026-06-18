# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxino16b.c

Dummy build-time stub for unsupported 16-bit image sample unpacking.

Key behavior:
- Includes Ghostscript base/sample type headers.
- Defines `sample_unpack_16_proc` as `0`.

Notable dependencies:
- `gxsample.h` for `sample_unpack_proc_t`.

Research notes:
- The common image setup path checks this pointer for 16-bit samples; this stub disables 16-bit unpacking in builds that use it.
