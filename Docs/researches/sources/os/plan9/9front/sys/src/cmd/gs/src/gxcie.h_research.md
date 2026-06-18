# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcie.h

Internal CIE color implementation declarations.

Key behavior:
- Declares CIE color-space init, restrict, install, concretize, remap, and concrete-space procedures used by Ghostscript color-space type tables.
- Provides `gx_cie_to_xyz_alloc`/`gx_cie_to_xyz_free`, a semi-special imager-state setup for PDF writer CIE-to-XYZ concretization.
- Defines `CIE_CHECK_RENDERING`, which returns black if no CIE rendering is installed and otherwise completes joint caches before remapping.
- Declares generic and concrete CIE remap-finish procedures, including real rendering and XYZ-only variants.
- Exposes GC descriptors for common CIE data structures.
- Declares helpers to set common defaults, load common caches, complete common CIE caches, install indirect CIE color spaces, and build common CIE color-space storage.

Dependencies:
- Includes `gscie.h` and depends on Ghostscript color-space procedure declaration macros, `gs_imager_state`, `gs_color_space`, `gs_state`, and CIE cache types.

Research notes:
- Comments document historical external-name length constraints, which explain the shorter `CIExxx` naming.
- The rendering check macro has control-flow effects via the caller-provided `do_exit`, so callers must read it as more than a pure predicate.
