# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevmem.c

## Role

`gsdevmem.c` creates and initializes Ghostscript memory/image devices from an initial matrix, dimensions, and palette/true-color descriptor.

## Main Functions

- `gs_initialize_wordimagedevice(...)` initializes caller-allocated `gx_device_memory`.
- `gs_makewordimagedevice(...)` allocates a memory device and delegates initialization.

`gs_makeimagedevice` is a macro in `gsdevice.h` over `gs_makewordimagedevice`.

## Behavior

The initializer maps `colors_size` to bit depth:

- palette sizes for 1/2/4/8-bit gray or RGB
- `-16`, `-24`, `-32` for true-color devices

For palette devices it validates that the palette includes black/white and, if colored, the RGB primaries. It picks word-oriented or byte-oriented memory-device prototypes by bit depth.

It validates the matrix is orthogonal, derives DPI from matrix scale, initializes device retention/refcount, sets the initial matrix, resolution, width/height, imaging bounding box, and bitmap memory. The bitmap itself is allocated on open.

## Dependencies

Uses matrix math, memory-device prototypes (`gxdevmem.h`), arithmetic helpers, error codes, and `gx_device_set_width_height`.

## Risks

Palette validation is strict and rejects palettes lacking required primaries. Non-orthogonal matrices return `undefinedresult`. For non-1-bit devices, palette allocation happens before `gs_make_mem_device`; later failures are minimal, but ownership must remain with the device.
