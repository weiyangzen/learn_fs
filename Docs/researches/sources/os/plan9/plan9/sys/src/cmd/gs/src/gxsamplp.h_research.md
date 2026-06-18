# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsamplp.h

`gxsamplp.h` is a multi-include template used by `gxsample.c` to generate sample unpacking functions. Callers must define `MULTIPLE_MAPS` and function-name macros for 1/2/4/8-bit variants before inclusion.

For `MULTIPLE_MAPS`, the template advances through per-component sample maps modulo `num_components_per_plane`; otherwise it uses one map. It generates functions for 1-bit, 2-bit, 4-bit, and 8-bit samples.

The 1-bit unpacker either expands nibbles through `lookup4x1to32` when `spread == 1`, or writes each bit-expanded byte at `spread` intervals through `lookup8`. The 2-bit unpacker similarly uses `lookup2x2to16` for packed spread-1 output or byte lookups for spread output. The 4-bit unpacker maps high/low nibbles. The 8-bit unpacker can return the original source pointer when spread is 1 and the map is identity, avoiding copying.

Each generated function updates `*pdata_x` to the residual bit/sample offset and returns the buffer or source pointer. Risk areas are alignment casts to `bits32`/`bits16`, reliance on caller-provided buffer size, and template macro hygiene.
