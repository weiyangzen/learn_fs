# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscspace.h

## Role

`gscspace.h` is the public color-space model definition for Ghostscript. It defines color-space indexes, storage hierarchy, shared parameter structs, and the client API for constructing and inspecting color spaces.

## Data Model

The header explains the historical embedded-storage design:

- small base spaces: DeviceGray/RGB/CMYK/Pixel and CIE spaces
- regular base spaces: small base spaces plus ICCBased
- direct spaces: base plus Separation and DeviceN
- paint spaces: direct plus Indexed
- general spaces: paint plus Pattern

Because subspaces are stored inline rather than through uniform pointers, each level has a larger struct type. The header explicitly warns that assignment must copy according to the actual source type size and that callers are responsible for fitting source objects into destination storage.

## Key Types

Defines `gs_color_space_index`, `gs_color_space_type`, `gs_color_space`, `gs_small_base_color_space`, `gs_base_color_space`, `gs_direct_color_space`, and `gs_paint_color_space`.

It also defines parameter structs for DevicePixel, ICCBased, Separation, DeviceN, Indexed, and Pattern spaces. Separation and DeviceN include colorant-name callbacks and flags for forcing alternate color-space use.

## API

Exposes device color-space initializers/builders, copy/assign/release helpers, index/component accessors, equality declaration, legal color restriction, and base/alternate-space retrieval.

## Dependencies

Includes `gsmemory.h` and `gsiparam.h`; references CIE, ICC, DeviceN map, client color, and GC descriptor types defined elsewhere.

## Risks

The inline hierarchy is memory-sensitive and type-size-sensitive. The comments note incomplete reference management for some non-scalar parameters, especially Indexed lookup tables and deeper compound parameters.
