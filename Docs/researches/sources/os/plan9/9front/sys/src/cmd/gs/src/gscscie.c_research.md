# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscscie.c

## Role

`gscscie.c` defines Ghostscript CIE color-space types, constructors, defaults, reference counting, concrete-space selection, lookup-table setup, and serialization.

This is color-management/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_color_space_type_CIEDEFG`
- `gs_color_space_type_CIEDEF`
- `gs_color_space_type_CIEABC`
- `gs_color_space_type_CIEA`
- `gx_concrete_space_CIE`
- `gx_install_CIE`
- `gx_set_common_cie_defaults`
- `gx_build_cie_space`
- `gs_cspace_build_CIEA`
- `gs_cspace_build_CIEABC`
- `gs_cspace_build_CIEDEF`
- `gs_cspace_build_CIEDEFG`
- `gs_cie_defx_set_lookup_table`
- `gx_serialize_cie_common_elements`

## Core Behavior

The file declares GC descriptors and four CIE color-space types for CIEBasedA, CIEBasedABC, CIEBasedDEF, and CIEBasedDEFG. Each type installs CIE initialization, restriction, concretization, overprint, reference-count adjustment, and serialization handlers.

`gx_concrete_space_CIE` chooses DeviceRGB unless the current CRD has a render table with four output components, in which case it chooses DeviceCMYK.

Constructors allocate both a color-space object and the large reference-counted parameter object, then apply default ranges, matrices, decode functions, install hooks, and lookup-table placeholders.

DEF/DEFG lookup-table setup stores dimensions and a pointer to the table but does not deep-copy table data.

Serialization emits color-space type, common CIE elements, cached decode values where needed, ranges, matrices, and lookup-table metadata/data.

## Dependencies

Uses CIE definitions, color-space internals, device color mapping, stream serialization, refcount/GC support, and CIE map/concretization routines.

## Notable Risks

- `gx_concrete_space_CIE` uses static `rgb_cs` and `cmyk_cs` objects initialized idempotently; shared mutable statics can be risky in concurrent contexts.
- `gx_serialize_lookup_table` writes `&t->table->data` rather than `t->table->data`, which appears suspicious because it serializes bytes from the address of the pointer field, not from the pointed-to table data.
- `gx_serialize_CIEDEFG` loops `k < 3` over `DecodeDEFG` caches even though DEFG has four components; this appears to omit the fourth cache.
- Lookup-table setters store caller-provided table pointers without ownership transfer.
