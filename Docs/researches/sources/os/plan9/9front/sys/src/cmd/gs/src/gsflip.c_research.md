# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsflip.c

## Role

`gsflip.c` converts planar image sample data from MultipleDataSource format into chunky/interleaved sample order for image processing.

This is image data layout support, not filesystem code.

## Main Interface

- `image_flip_planes`

## Core Behavior

Specialized fast paths handle:

- 3 planes at 1, 2, 4, 8, and 12 bits/sample
- 4 planes at 1, 2, 4, 8, and 12 bits/sample

Generic slower paths handle DeviceN-style arbitrary plane counts for 1, 2, 4, 8, and 12 bits/sample.

The code uses:

- static lookup tables for 3-plane 1-bit and 2-bit packing
- bit-transpose macros for some 4-plane paths
- `sample_store_*` macros from `gsbitops.h` for generic packing

## Important Semantics

- `bits_per_sample` must be 1, 2, 4, 8, or 12.
- For 12-bit input, the implementation assumes an integral number of pixels and rounds processing in 3-byte groups.
- Invalid plane count or unsupported sample depth returns `-1`.

## Notable Risks

- Bounds checking is delegated to callers: `nbytes`, plane pointers, and output buffer size must already be correct.
- Generic paths are intentionally slow but used for arbitrary DeviceN plane counts.
- The dispatch tables include `flip_fail` entries for unsupported bit depths.
