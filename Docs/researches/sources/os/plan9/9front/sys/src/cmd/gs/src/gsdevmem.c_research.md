# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdevmem.c

This file creates and initializes Ghostscript memory/image devices.

Main functions:
- `gs_initialize_wordimagedevice` initializes caller-provided `gx_device_memory`.
- `gs_makewordimagedevice` allocates a `gx_device_memory` and delegates initialization.

Key behavior:
- Interprets `colors_size` as palette size for indexed devices or `-16`, `-24`, `-32` for true-color devices.
- Selects a memory-device prototype by bits per pixel and word-orientation.
- Validates palettes, requiring black/white for grayscale and full primaries for color palettes.
- Determines monochrome polarity from the palette.
- Allocates and copies palette data for paletted devices.
- Downgrades color metadata to grayscale when a palette has no real color.
- Validates that the supplied matrix is orthogonal and computes DPI from user-unit scale.
- Sets media size, resolution, initial matrix, imaging bounding box, retained/reference-count state, and bitmap memory.

The device is left closed; its bitmap allocation happens when opened. This separation supports callers that want allocation and initialization as distinct steps.
