# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscscie.c

## Purpose
Defines and constructs Ghostscript CIE color spaces.

## Key Behavior
- Defines GC descriptors for CIE common elements and CIEA/ABC/DEF/DEFG structures.
- Defines color-space type descriptors for:
  - CIEBasedA,
  - CIEBasedABC,
  - CIEBasedDEF,
  - CIEBasedDEFG.
- Implements `gx_concrete_space_CIE`, selecting DeviceRGB unless the current CRD RenderTable outputs 4 components.
- Provides `gx_install_CIE`, which dispatches through the color space’s `install_cspace` hook.
- Adjusts reference counts for each CIE parameter structure.
- Sets common and ABC default values.
- Builds CIE color spaces and parameter structures.
- Assigns lookup tables for CIEDEF/CIEDEFG.
- Serializes CIE common data and each CIE color-space variant.

## Important Details
- Common default WhitePoint is set to BlackPoint because there is no valid default; comments note using such a space gives poor results.
- CIEDEF and CIEDEFG default lookup tables are placeholders intended to fail predictably unless replaced.
- `gx_build_cie_space` is exported for ICC support.
- CIE spaces use `gx_spot_colors_set_overprint`.

## Dependencies
Uses CIE cache structures, color-space internals, device color mapping, graphics-state internals, stream serialization, and refcount/GC helpers.

## Research Notes
Two serialization details look suspicious in this snapshot:
- `gx_serialize_CIEDEFG` serializes only three `DecodeDEFG` caches despite DEFG having four decode components.
- `gx_serialize_lookup_table` writes from `&t->table->data` with `t->table->size`, which appears to write bytes from the pointer field rather than from the table data buffer.
