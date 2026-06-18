# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcspace.h

## Purpose
Defines the internal color-space type/class interface for Ghostscript color-space implementations.

## Public Surface
- `gs_color_space_type_s`: color-space vtable with index, base/alternate eligibility flags, structure type, component count, base-space lookup, color initialization/restriction, concrete-space lookup, concretization, concrete remap, direct remap, install, overprint setup, reference-count adjustment, serialization, and linearity checking.
- Macros for invoking color-space procedures, including `cs_num_components`, `cs_base_space`, `cs_init_color`, `cs_restrict_color`, `cs_concrete_space`, `cs_concretize_color`, `cs_adjust_counts`, and `cs_serialize`.
- Standard procedure declarations for 1/3/4-component spaces, no-base/no-concrete/default-remap helpers, reference-count no-ops, serialization, linearity checks, and overprint.
- Device color-space remap/concretize declarations implemented in `gxcmap.c`.
- Allocation/init API: `gs_cspace_init` and `gs_cspace_alloc`.

## Semantics
- Concrete colors are values the device can handle directly, possibly after halftoning.
- Pattern spaces have component counts encoded specially: `-1` for colored patterns and `-N-1` for uncolored patterns.
- Reference counting is split between indirect color-space components and indirect color values.
- Serialization excludes the type pointer because it is assumed to be handled separately as a static constant.

## Dependencies
Uses public color-space/client-color definitions, concrete fraction types, color selection, streams, devices, imager state, and Ghostscript memory descriptors.

## Risks and Notes
- Many procedures are not defined for Pattern spaces or non-concrete spaces; callers must dispatch through the correct color-space type.
- The `adjust_color_count` procedure explicitly accepts a NULL color-space argument for a documented application hack around Pattern color release.

Filesystem relevance: none. This is color-space implementation infrastructure.
