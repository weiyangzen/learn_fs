# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcspace.h

Internal color-space type/class interface.

Key contents:
- Defines `gs_color_space_type_s`, the method table for all color-space implementations.
- Records color-space index, base/alternate-space eligibility, concrete structure type, and method pointers.
- Methods include component count, base-space access, initial color, restriction, concrete-space lookup, concretization, concrete remap, direct remap, install, overprint setup, cspace/color reference-count adjustment, serialization, and linearity testing.
- Provides macros for invoking each method.
- Declares standard structure descriptors and standard helper procedures for common component counts, init/restrict behavior, no-op/default behavior, serialization, and linearity.
- Declares DeviceGray/RGB/CMYK concretize/remap implementations from `gxcmap.c`.
- Declares `gs_cspace_init` and `gs_cspace_alloc`.

Notable dependencies:
- Client color-space API, client color values, color selection, and fraction types.

Research notes:
- This header is the core internal abstraction that lets `gxcmap.c`, `gxclrast.c`, and color-space implementations share a uniform color-space method table.
- Pattern spaces are special because component counts can depend on an underlying space.
